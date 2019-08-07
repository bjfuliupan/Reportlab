# -*- coding: utf-8 -*-

import xmltodict
from copy import deepcopy
from reportlab.graphics.shapes import Drawing, String, STATE_DEFAULTS, Line, Rect
from reportlab.lib.validators import isListOfNumbers, isString, isNumber, isListOfStrings
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.colors import Color
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import Table, TableStyle

from pdflib.ReportLabLineCharts import ReportLabHorizontalLineChart
from pdflib.ReportLabBarCharts import ReportLabHorizontalBarChart, ReportLabVerticalBarChart
from pdflib.ReportLabPieCharts import ReportLabPieChart
from pdflib.ReportLabLib import DefaultFontName, list_eval, color_eval, bool_eval

from abc import ABC, abstractmethod


class PDFTemplateConstant(object):

    PDF_FILE_NAME = "file_name"
    PDF_AUTHOR = "author"
    PDF_TITLE = "title"
    PDF_PAGE_SIZE = "page_size"
    PDF_COORDINATE = "coordinate"
    PDF_HEADER_TEXT = "header_text"
    PDF_SHOW_BORDER = "show_border"

    PDF_PAGES = "pages"
    PDF_RECT = "rect"
    PDF_AUTO_POSITION = "auto_position"
    PDF_PAGE_PADDING_X = "x-padding"
    PDF_PAGE_PADDING_Y = "y-padding"
    PDF_ALIGN_TYPE = "align-type"
    PDF_INVALID = "invalid"

    PDF_ITEMS = "items"
    PDF_ITEM_TYPE = "type"
    PDF_ITEM_CONTENT = "content"
    PDF_ITEM_DATA = "data"
    PDF_POSITION = "position"
    PDF_FONT_NAME = "font_name"
    PDF_FONT_COLOR = "font_color"
    PDF_FONT_SIZE = "font_size"
    PDF_ITEM_MARGIN_LEFT = "margin-left"
    PDF_ITEM_MARGIN_RIGHT = "margin-right"
    PDF_ITEM_MARGIN_TOP = "margin-top"
    PDF_ITEM_MARGIN_BOTTOM = "margin-bottom"
    PDF_PARAGRAPH_INDENT = "indent_flag"
    PDF_CHART_MAIN_TITLE = "main_title"
    PDF_CHART_MT_FONT_NAME = "main_title_font_name"
    PDF_CHART_MT_FONT_COLOR = "main_title_font_color"
    PDF_CHART_MT_FONT_SIZE = "main_title_font_size"
    PDF_CHART_X_DESC = "x_desc"
    PDF_CHART_Y_DESC = "y_desc"
    PDF_CHART_CAT_NAMES = "category_names"
    PDF_CHART_LEGEND_NAMES = "legend_names"
    PDF_CHART_LEGEND_POSITION = "legend_position"
    PDF_CHART_LEGEND_ADJUST_X = "legend_adjust_x"
    PDF_CHART_LEGEND_ADJUST_Y = "legend_adjust_y"
    PDF_CHART_STEP_COUNT = "step_count"
    PDF_CHART_CAT_LABEL_ALL = "cat_label_all"
    PDF_CHART_CAT_LABEL_ANGLE = "cat_label_angle"
    PDF_BAR_BAR_STYLE = "bar_style"
    PDF_BAR_STYLE = "style"
    PDF_PARAGRAPH_STYLE = "style"
    PDF_BAR_LABEL_FORMAT = "label_format"
    PDF_TABLE_COLUMNS = "columns"
    PDF_TABLE_COL_WIDTHS = "col_widths"

    PDF_ITEM_TYPE_LINE_CHART = "line_chart"
    PDF_ITEM_TYPE_BAR_CHART = "bar_chart"
    PDF_ITEM_TYPE_PIE_CHART = "pie_chart"
    PDF_ITEM_TYPE_TEXT = "text"
    PDF_ITEM_TYPE_PARAGRAPH = "paragraph"
    PDF_ITEM_TYPE_TABLE = "table"

    def __init__(self):
        pass


class PDFTemplateItem(ABC):
    """
    Item基类
    """

    def __init__(self, item_content):
        self.item_content = deepcopy(item_content)

        self.format_content(self.item_content)
        self.args_check(self.item_content)

    @staticmethod
    def format_content(item_content):
        if PDFTemplateConstant.PDF_RECT in item_content and \
                isinstance(item_content[PDFTemplateConstant.PDF_RECT], str):
            item_content[PDFTemplateConstant.PDF_RECT] = list_eval(item_content[PDFTemplateConstant.PDF_RECT])

        if PDFTemplateConstant.PDF_ITEM_MARGIN_LEFT in item_content:
            item_content[PDFTemplateConstant.PDF_ITEM_MARGIN_LEFT] = \
                int(item_content[PDFTemplateConstant.PDF_ITEM_MARGIN_LEFT])
        else:
            item_content[PDFTemplateConstant.PDF_ITEM_MARGIN_LEFT] = 0
        if PDFTemplateConstant.PDF_ITEM_MARGIN_RIGHT in item_content:
            item_content[PDFTemplateConstant.PDF_ITEM_MARGIN_RIGHT] = \
                int(item_content[PDFTemplateConstant.PDF_ITEM_MARGIN_RIGHT])
        else:
            item_content[PDFTemplateConstant.PDF_ITEM_MARGIN_RIGHT] = 0
        if PDFTemplateConstant.PDF_ITEM_MARGIN_TOP in item_content:
            item_content[PDFTemplateConstant.PDF_ITEM_MARGIN_TOP] = \
                int(item_content[PDFTemplateConstant.PDF_ITEM_MARGIN_TOP])
        else:
            item_content[PDFTemplateConstant.PDF_ITEM_MARGIN_TOP] = 0
        if PDFTemplateConstant.PDF_ITEM_MARGIN_BOTTOM in item_content:
            item_content[PDFTemplateConstant.PDF_ITEM_MARGIN_BOTTOM] = \
                int(item_content[PDFTemplateConstant.PDF_ITEM_MARGIN_BOTTOM])
        else:
            item_content[PDFTemplateConstant.PDF_ITEM_MARGIN_BOTTOM] = 0

        if PDFTemplateConstant.PDF_INVALID not in item_content:
            item_content[PDFTemplateConstant.PDF_INVALID] = False
        elif not isinstance(item_content[PDFTemplateConstant.PDF_INVALID], bool):
            if item_content[PDFTemplateConstant.PDF_INVALID] == "True":
                item_content[PDFTemplateConstant.PDF_INVALID] = True
            elif item_content[PDFTemplateConstant.PDF_INVALID] == "False":
                item_content[PDFTemplateConstant.PDF_INVALID] = False
            else:
                item_content[PDFTemplateConstant.PDF_INVALID] = False

    @staticmethod
    def args_check(item_content):
        if not isinstance(item_content, dict):
            raise ValueError("item content is not dict json.")

        if PDFTemplateConstant.PDF_ITEM_TYPE not in item_content:
            raise ValueError("no %s." % PDFTemplateConstant.PDF_ITEM_TYPE)

        if PDFTemplateConstant.PDF_RECT not in item_content or \
                not isListOfNumbers(item_content[PDFTemplateConstant.PDF_RECT]) or \
                len(item_content[PDFTemplateConstant.PDF_RECT]) != 4:
            raise ValueError("item %s format error." % PDFTemplateConstant.PDF_RECT)

        if PDFTemplateConstant.PDF_INVALID not in item_content:
            raise ValueError("no %s." % PDFTemplateConstant.PDF_INVALID)
        if not isinstance(item_content[PDFTemplateConstant.PDF_INVALID], bool):
            raise ValueError("the type of %s is not bool." % PDFTemplateConstant.PDF_INVALID)

        if PDFTemplateConstant.PDF_ITEM_MARGIN_LEFT not in item_content:
            raise ValueError("no %s." % PDFTemplateConstant.PDF_ITEM_MARGIN_LEFT)
        if not isinstance(item_content[PDFTemplateConstant.PDF_ITEM_MARGIN_LEFT], int):
            raise ValueError("the type of %s is not int." % PDFTemplateConstant.PDF_ITEM_MARGIN_LEFT)

        if PDFTemplateConstant.PDF_ITEM_MARGIN_RIGHT not in item_content:
            raise ValueError("no %s." % PDFTemplateConstant.PDF_ITEM_MARGIN_RIGHT)
        if not isinstance(item_content[PDFTemplateConstant.PDF_ITEM_MARGIN_RIGHT], int):
            raise ValueError("the type of %s is not int." % PDFTemplateConstant.PDF_ITEM_MARGIN_RIGHT)

        if PDFTemplateConstant.PDF_ITEM_MARGIN_TOP not in item_content:
            raise ValueError("no %s." % PDFTemplateConstant.PDF_ITEM_MARGIN_TOP)
        if not isinstance(item_content[PDFTemplateConstant.PDF_ITEM_MARGIN_TOP], int):
            raise ValueError("the type of %s is not int." % PDFTemplateConstant.PDF_ITEM_MARGIN_TOP)

        if PDFTemplateConstant.PDF_ITEM_MARGIN_BOTTOM not in item_content:
            raise ValueError("no %s." % PDFTemplateConstant.PDF_ITEM_MARGIN_BOTTOM)
        if not isinstance(item_content[PDFTemplateConstant.PDF_ITEM_MARGIN_BOTTOM], int):
            raise ValueError("the type of %s is not int." % PDFTemplateConstant.PDF_ITEM_MARGIN_BOTTOM)

    def get_rect(self):
        return self.item_content[PDFTemplateConstant.PDF_RECT][0], \
               self.item_content[PDFTemplateConstant.PDF_RECT][1], \
               self.item_content[PDFTemplateConstant.PDF_RECT][2], \
               self.item_content[PDFTemplateConstant.PDF_RECT][3]

    def set_rect(self, x=None, y=None, width=None, height=None):
        if x:
            self.item_content[PDFTemplateConstant.PDF_RECT][0] = x
        if y:
            self.item_content[PDFTemplateConstant.PDF_RECT][1] = y
        if width:
            self.item_content[PDFTemplateConstant.PDF_RECT][2] = width
        if height:
            self.item_content[PDFTemplateConstant.PDF_RECT][3] = height

    @staticmethod
    def auto_set_height(item):
        pass

    @staticmethod
    def split_by_height(items, index, page_height):
        return False

    @staticmethod
    def _draw_text(format_json, auto_calc=True):
        """
        生成Text对象
        :param format_json:
        :param auto_calc:
        :return:
        """
        width = format_json[PDFTemplateConstant.PDF_RECT][2]
        height = format_json[PDFTemplateConstant.PDF_RECT][3]

        d = Drawing(width, height, vAlign="TOP")

        content = format_json[PDFTemplateConstant.PDF_ITEM_CONTENT]
        position = format_json[PDFTemplateConstant.PDF_POSITION]
        x = 0
        y = 0

        font_size = STATE_DEFAULTS['fontSize']
        if PDFTemplateConstant.PDF_FONT_SIZE in format_json:
            font_size = format_json[PDFTemplateConstant.PDF_FONT_SIZE]

        if auto_calc:
            if position == "middle":
                x = int(width / 2)
                y = int(height / 2) - int(font_size / 2)
            elif position == "start":
                y = height
        else:
            x = format_json[PDFTemplateConstant.PDF_RECT][0]
            y = format_json[PDFTemplateConstant.PDF_RECT][1]

        text = String(x, y, content)

        text.fontName = DefaultFontName
        if PDFTemplateConstant.PDF_FONT_NAME in format_json:
            text.fontName = format_json[PDFTemplateConstant.PDF_FONT_NAME]
        text.fontSize = font_size
        if PDFTemplateConstant.PDF_FONT_COLOR in format_json:
            text.fillColor = format_json[PDFTemplateConstant.PDF_FONT_COLOR]
        text.textAnchor = position

        d.add(text)

        return d

    @staticmethod
    def _draw_item_rect(d, x, y, width, height, format_json):
        r = Rect(x, y, width, height, fillColor=Color(0.95, 0.95, 0.95, 1))
        d.add(r)

        width += 40
        height += 40
        text_format = {PDFTemplateConstant.PDF_RECT: [int(width / 2), int(height / 2), width, height],
                       PDFTemplateConstant.PDF_ITEM_CONTENT: "暂无数据", PDFTemplateConstant.PDF_POSITION: "middle",
                       PDFTemplateConstant.PDF_FONT_NAME: DefaultFontName, PDFTemplateConstant.PDF_FONT_SIZE: 30,
                       PDFTemplateConstant.PDF_FONT_COLOR: Color(0.5, 0.5, 0.5, 1)}
        t = PDFTemplateItem._draw_text(text_format)
        d.add(t)

        if PDFTemplateConstant.PDF_CHART_MAIN_TITLE in format_json:
            text_format = {PDFTemplateConstant.PDF_RECT: [0, height, width, height - 15],
                           PDFTemplateConstant.PDF_ITEM_CONTENT: format_json[PDFTemplateConstant.PDF_CHART_MAIN_TITLE],
                           PDFTemplateConstant.PDF_POSITION: "start",
                           PDFTemplateConstant.PDF_FONT_NAME: DefaultFontName,
                           PDFTemplateConstant.PDF_FONT_SIZE: 15,
                           PDFTemplateConstant.PDF_FONT_COLOR: Color(0.5, 0.5, 0.5, 1)}
            if PDFTemplateConstant.PDF_CHART_MT_FONT_NAME in format_json:
                text_format[PDFTemplateConstant.PDF_FONT_NAME] = \
                    format_json[PDFTemplateConstant.PDF_CHART_MT_FONT_NAME]
            if PDFTemplateConstant.PDF_CHART_MT_FONT_SIZE in format_json:
                text_format[PDFTemplateConstant.PDF_FONT_SIZE] = \
                    format_json[PDFTemplateConstant.PDF_CHART_MT_FONT_SIZE]
            if PDFTemplateConstant.PDF_CHART_MT_FONT_COLOR in format_json:
                text_format[PDFTemplateConstant.PDF_FONT_COLOR] = \
                    format_json[PDFTemplateConstant.PDF_CHART_MT_FONT_COLOR]
            main_title = PDFTemplateItem._draw_text(text_format)
            d.add(main_title)

    @staticmethod
    def draw_border(cv, x, y, width, height, color, stroke_width=1):
        d = Drawing(width, height)
        r = Rect(0, 0, width, height, strokeWidth=stroke_width, strokeColor=color, fillColor=Color(0, 0, 0, 0))
        d.add(r)
        d.drawOn(cv, x, y)

    @abstractmethod
    def draw(self, cv, show_border=False):
        if show_border:
            self.draw_border(cv, self.item_content[PDFTemplateConstant.PDF_RECT][0],
                             self.item_content[PDFTemplateConstant.PDF_RECT][1],
                             self.item_content[PDFTemplateConstant.PDF_RECT][2],
                             self.item_content[PDFTemplateConstant.PDF_RECT][3],
                             Color(1, 0, 0, 1))


class PDFTemplateLineChart(PDFTemplateItem):
    """
    折线图
    """

    def __init__(self, item_content):
        PDFTemplateItem.__init__(self, item_content)

    @staticmethod
    def format_content(item_content):
        """
        格式化相关数据
        :param item_content:
        :return:
        """
        PDFTemplateItem.format_content(item_content)

        if PDFTemplateConstant.PDF_ITEM_DATA in item_content and \
                isinstance(item_content[PDFTemplateConstant.PDF_ITEM_DATA], str):
            item_content[PDFTemplateConstant.PDF_ITEM_DATA] = \
                list_eval(item_content[PDFTemplateConstant.PDF_ITEM_DATA])
        if PDFTemplateConstant.PDF_CHART_MT_FONT_SIZE in item_content:
            item_content[PDFTemplateConstant.PDF_CHART_MT_FONT_SIZE] = \
                int(item_content[PDFTemplateConstant.PDF_CHART_MT_FONT_SIZE])
        if PDFTemplateConstant.PDF_CHART_MT_FONT_COLOR in item_content and \
                isinstance(item_content[PDFTemplateConstant.PDF_CHART_MT_FONT_COLOR], str):
            item_content[PDFTemplateConstant.PDF_CHART_MT_FONT_COLOR] = \
                color_eval(item_content[PDFTemplateConstant.PDF_CHART_MT_FONT_COLOR])
        if PDFTemplateConstant.PDF_CHART_CAT_NAMES in item_content and \
                isString(item_content[PDFTemplateConstant.PDF_CHART_CAT_NAMES]):
            item_content[PDFTemplateConstant.PDF_CHART_CAT_NAMES] = \
                list_eval(item_content[PDFTemplateConstant.PDF_CHART_CAT_NAMES])
        if PDFTemplateConstant.PDF_CHART_CAT_LABEL_ANGLE in item_content:
            item_content[PDFTemplateConstant.PDF_CHART_CAT_LABEL_ANGLE] = \
                int(item_content[PDFTemplateConstant.PDF_CHART_CAT_LABEL_ANGLE])
        if PDFTemplateConstant.PDF_CHART_CAT_LABEL_ALL in item_content and \
                not isinstance(item_content[PDFTemplateConstant.PDF_CHART_CAT_LABEL_ALL], bool):
            if item_content[PDFTemplateConstant.PDF_CHART_CAT_LABEL_ALL] == "True":
                item_content[PDFTemplateConstant.PDF_CHART_CAT_LABEL_ALL] = True
            elif item_content[PDFTemplateConstant.PDF_CHART_CAT_LABEL_ALL] == "False":
                item_content[PDFTemplateConstant.PDF_CHART_CAT_LABEL_ALL] = False
        if PDFTemplateConstant.PDF_CHART_LEGEND_NAMES in item_content and \
                isinstance(item_content[PDFTemplateConstant.PDF_CHART_LEGEND_NAMES], str):
            item_content[PDFTemplateConstant.PDF_CHART_LEGEND_NAMES] = \
                list_eval(item_content[PDFTemplateConstant.PDF_CHART_LEGEND_NAMES])
        if PDFTemplateConstant.PDF_CHART_LEGEND_ADJUST_X in item_content:
            item_content[PDFTemplateConstant.PDF_CHART_LEGEND_ADJUST_X] = \
                int(item_content[PDFTemplateConstant.PDF_CHART_LEGEND_ADJUST_X])
        if PDFTemplateConstant.PDF_CHART_LEGEND_ADJUST_Y in item_content:
            item_content[PDFTemplateConstant.PDF_CHART_LEGEND_ADJUST_Y] = \
                int(item_content[PDFTemplateConstant.PDF_CHART_LEGEND_ADJUST_Y])
        if PDFTemplateConstant.PDF_CHART_STEP_COUNT in item_content:
            item_content[PDFTemplateConstant.PDF_CHART_STEP_COUNT] = \
                int(item_content[PDFTemplateConstant.PDF_CHART_STEP_COUNT])

    @staticmethod
    def args_check(item_content):
        """
        相关参数校验
        :param item_content:
        :return:
        """
        PDFTemplateItem.args_check(item_content)

        if PDFTemplateConstant.PDF_ITEM_DATA not in item_content:
            raise ValueError("line chart no %s." % PDFTemplateConstant.PDF_ITEM_DATA)
        if item_content[PDFTemplateConstant.PDF_ITEM_DATA] and \
                not isinstance(item_content[PDFTemplateConstant.PDF_ITEM_DATA], list):
            raise ValueError("line chart %s format error." % PDFTemplateConstant.PDF_ITEM_DATA)
        if PDFTemplateConstant.PDF_CHART_MT_FONT_SIZE in item_content and \
                not isinstance(item_content[PDFTemplateConstant.PDF_CHART_MT_FONT_SIZE], int):
            raise ValueError("line chart %s format error." % PDFTemplateConstant.PDF_CHART_MT_FONT_SIZE)
        if PDFTemplateConstant.PDF_CHART_MT_FONT_COLOR in item_content and \
                not isinstance(item_content[PDFTemplateConstant.PDF_CHART_MT_FONT_COLOR], Color):
            raise ValueError("line chart %s format error." % PDFTemplateConstant.PDF_CHART_MT_FONT_COLOR)
        if PDFTemplateConstant.PDF_CHART_CAT_NAMES in item_content and \
                not isinstance(item_content[PDFTemplateConstant.PDF_CHART_CAT_NAMES], list):
            raise ValueError("line chart %s format error." % PDFTemplateConstant.PDF_CHART_CAT_NAMES)
        if PDFTemplateConstant.PDF_CHART_CAT_LABEL_ANGLE in item_content and \
                not isinstance(item_content[PDFTemplateConstant.PDF_CHART_CAT_LABEL_ANGLE], int):
            raise ValueError("line chart %s format error." % PDFTemplateConstant.PDF_CHART_CAT_LABEL_ANGLE)
        if PDFTemplateConstant.PDF_CHART_CAT_LABEL_ALL in item_content and \
                not isinstance(item_content[PDFTemplateConstant.PDF_CHART_CAT_LABEL_ALL], bool):
            raise ValueError("line chart %s format error." % PDFTemplateConstant.PDF_CHART_CAT_LABEL_ALL)
        if PDFTemplateConstant.PDF_CHART_LEGEND_NAMES in item_content and \
                not isinstance(item_content[PDFTemplateConstant.PDF_CHART_LEGEND_NAMES], list):
            raise ValueError("line chart %s format error." % PDFTemplateConstant.PDF_CHART_LEGEND_NAMES)
        if PDFTemplateConstant.PDF_CHART_LEGEND_ADJUST_X in item_content and \
                not isinstance(item_content[PDFTemplateConstant.PDF_CHART_LEGEND_ADJUST_X], int):
            raise ValueError("line chart %s format error." % PDFTemplateConstant.PDF_CHART_LEGEND_ADJUST_X)
        if PDFTemplateConstant.PDF_CHART_LEGEND_ADJUST_Y in item_content and \
                not isinstance(item_content[PDFTemplateConstant.PDF_CHART_LEGEND_ADJUST_Y], int):
            raise ValueError("line chart %s format error." % PDFTemplateConstant.PDF_CHART_LEGEND_ADJUST_Y)
        if PDFTemplateConstant.PDF_CHART_STEP_COUNT in item_content and \
                not isinstance(item_content[PDFTemplateConstant.PDF_CHART_STEP_COUNT], int):
            raise ValueError("line chart %s format error." % PDFTemplateConstant.PDF_CHART_STEP_COUNT)

    @staticmethod
    def _draw_line_chart(format_json):
        """
        生成折线图对象
        :param format_json:
        :return:
        """
        width = format_json[PDFTemplateConstant.PDF_RECT][2]
        height = format_json[PDFTemplateConstant.PDF_RECT][3]

        d = Drawing(width, height, vAlign="TOP")

        if format_json[PDFTemplateConstant.PDF_ITEM_DATA] is None or \
                isinstance(format_json[PDFTemplateConstant.PDF_ITEM_DATA], str):
            PDFTemplateItem._draw_item_rect(d, 20, 20, width - 40, height - 50, format_json)
        elif type(format_json[PDFTemplateConstant.PDF_ITEM_DATA]) is list:
            cat_names = format_json[PDFTemplateConstant.PDF_CHART_CAT_NAMES]
            data = format_json[PDFTemplateConstant.PDF_ITEM_DATA]

            step_count = 4
            if PDFTemplateConstant.PDF_CHART_STEP_COUNT in format_json and \
                    isNumber(format_json[PDFTemplateConstant.PDF_CHART_STEP_COUNT]) is True:
                step_count = format_json[PDFTemplateConstant.PDF_CHART_STEP_COUNT]
            legend_names = None
            if PDFTemplateConstant.PDF_CHART_LEGEND_NAMES in format_json and \
                    isListOfStrings(format_json[PDFTemplateConstant.PDF_CHART_LEGEND_NAMES]) is True:
                legend_names = format_json[PDFTemplateConstant.PDF_CHART_LEGEND_NAMES]
            legend_position = "top-right"
            if PDFTemplateConstant.PDF_CHART_LEGEND_POSITION in format_json and \
                    isString(format_json[PDFTemplateConstant.PDF_CHART_LEGEND_POSITION]) is True:
                legend_position = format_json[PDFTemplateConstant.PDF_CHART_LEGEND_POSITION]
            legend_adjust_x = 0
            if PDFTemplateConstant.PDF_CHART_LEGEND_ADJUST_X in format_json and \
                    isNumber(format_json[PDFTemplateConstant.PDF_CHART_LEGEND_ADJUST_X]) is True:
                legend_adjust_x = format_json[PDFTemplateConstant.PDF_CHART_LEGEND_ADJUST_X]
            legend_adjust_y = 0
            if PDFTemplateConstant.PDF_CHART_LEGEND_ADJUST_Y in format_json and \
                    isNumber(format_json[PDFTemplateConstant.PDF_CHART_LEGEND_ADJUST_Y]) is True:
                legend_adjust_y = format_json[PDFTemplateConstant.PDF_CHART_LEGEND_ADJUST_Y]
            main_title = ""
            if PDFTemplateConstant.PDF_CHART_MAIN_TITLE in format_json and \
                    isString(format_json[PDFTemplateConstant.PDF_CHART_MAIN_TITLE]) is True:
                main_title = format_json[PDFTemplateConstant.PDF_CHART_MAIN_TITLE]
            main_title_font_name = None
            if PDFTemplateConstant.PDF_CHART_MT_FONT_NAME in format_json and \
                    isString(format_json[PDFTemplateConstant.PDF_CHART_MT_FONT_NAME]) is True:
                main_title_font_name = format_json[PDFTemplateConstant.PDF_CHART_MT_FONT_NAME]
            main_title_font_size = None
            if PDFTemplateConstant.PDF_CHART_MT_FONT_SIZE in format_json and \
                    isNumber(format_json[PDFTemplateConstant.PDF_CHART_MT_FONT_SIZE]) is True:
                main_title_font_size = format_json[PDFTemplateConstant.PDF_CHART_MT_FONT_SIZE]
            main_title_font_color = None
            if PDFTemplateConstant.PDF_CHART_MT_FONT_COLOR in format_json:
                main_title_font_color = format_json[PDFTemplateConstant.PDF_CHART_MT_FONT_COLOR]
            x_desc = None
            if PDFTemplateConstant.PDF_CHART_X_DESC in format_json and \
                    isString(format_json[PDFTemplateConstant.PDF_CHART_X_DESC]) is True:
                x_desc = format_json[PDFTemplateConstant.PDF_CHART_X_DESC]
            y_desc = None
            if PDFTemplateConstant.PDF_CHART_Y_DESC in format_json and \
                    isString(format_json[PDFTemplateConstant.PDF_CHART_Y_DESC]) is True:
                y_desc = format_json[PDFTemplateConstant.PDF_CHART_Y_DESC]
            cat_label_all = False
            if PDFTemplateConstant.PDF_CHART_CAT_LABEL_ALL in format_json:
                cat_label_all = format_json[PDFTemplateConstant.PDF_CHART_CAT_LABEL_ALL]
            cat_label_angle = 30
            if PDFTemplateConstant.PDF_CHART_CAT_LABEL_ANGLE in format_json and \
                    isNumber(format_json[PDFTemplateConstant.PDF_CHART_CAT_LABEL_ANGLE]) is True:
                cat_label_angle = format_json[PDFTemplateConstant.PDF_CHART_CAT_LABEL_ANGLE]

            line_chart = ReportLabHorizontalLineChart(0, 0, width, height, cat_names, data, step_count=step_count,
                                                      legend_names=legend_names, legend_position=legend_position,
                                                      legend_adjust_x=legend_adjust_x, legend_adjust_y=legend_adjust_y,
                                                      main_title=main_title, main_title_font_name=main_title_font_name,
                                                      main_title_font_size=main_title_font_size,
                                                      main_title_font_color=main_title_font_color,
                                                      x_desc=x_desc, y_desc=y_desc,
                                                      cat_label_angle=cat_label_angle, cat_label_all=cat_label_all)
            d.add(line_chart)

        return d

    def draw(self, cv, show_border=False):
        """
        画折线图
        :param cv:
        :param show_border:
        :return:
        """
        PDFTemplateItem.draw(self, cv, show_border)

        d = self._draw_line_chart(self.item_content)

        d.wrapOn(cv, self.item_content[PDFTemplateConstant.PDF_RECT][2],
                 self.item_content[PDFTemplateConstant.PDF_RECT][3])
        d.drawOn(cv, self.item_content[PDFTemplateConstant.PDF_RECT][0],
                 self.item_content[PDFTemplateConstant.PDF_RECT][1])


class PDFTemplateBarChart(PDFTemplateItem):
    """
    柱状图
    """

    def __init__(self, item_content):
        PDFTemplateItem.__init__(self, item_content)

    @staticmethod
    def format_content(item_content):
        """
        格式化相关数据
        :param item_content:
        :return:
        """
        PDFTemplateItem.format_content(item_content)

        if PDFTemplateConstant.PDF_ITEM_DATA in item_content and \
                isinstance(item_content[PDFTemplateConstant.PDF_ITEM_DATA], str):
            item_content[PDFTemplateConstant.PDF_ITEM_DATA] = \
                list_eval(item_content[PDFTemplateConstant.PDF_ITEM_DATA])
        if PDFTemplateConstant.PDF_CHART_MT_FONT_SIZE in item_content:
            item_content[PDFTemplateConstant.PDF_CHART_MT_FONT_SIZE] = \
                int(item_content[PDFTemplateConstant.PDF_CHART_MT_FONT_SIZE])
        if PDFTemplateConstant.PDF_CHART_MT_FONT_COLOR in item_content and \
                isinstance(item_content[PDFTemplateConstant.PDF_CHART_MT_FONT_COLOR], str):
            item_content[PDFTemplateConstant.PDF_CHART_MT_FONT_COLOR] = \
                color_eval(item_content[PDFTemplateConstant.PDF_CHART_MT_FONT_COLOR])
        if PDFTemplateConstant.PDF_CHART_CAT_NAMES in item_content and \
                isString(item_content[PDFTemplateConstant.PDF_CHART_CAT_NAMES]):
            item_content[PDFTemplateConstant.PDF_CHART_CAT_NAMES] = \
                list_eval(item_content[PDFTemplateConstant.PDF_CHART_CAT_NAMES])
        if PDFTemplateConstant.PDF_CHART_CAT_LABEL_ANGLE in item_content:
            item_content[PDFTemplateConstant.PDF_CHART_CAT_LABEL_ANGLE] = \
                int(item_content[PDFTemplateConstant.PDF_CHART_CAT_LABEL_ANGLE])
        if PDFTemplateConstant.PDF_CHART_CAT_LABEL_ALL in item_content and \
                not isinstance(item_content[PDFTemplateConstant.PDF_CHART_CAT_LABEL_ALL], bool):
            if item_content[PDFTemplateConstant.PDF_CHART_CAT_LABEL_ALL] == "True":
                item_content[PDFTemplateConstant.PDF_CHART_CAT_LABEL_ALL] = True
            elif item_content[PDFTemplateConstant.PDF_CHART_CAT_LABEL_ALL] == "False":
                item_content[PDFTemplateConstant.PDF_CHART_CAT_LABEL_ALL] = False
        if PDFTemplateConstant.PDF_CHART_LEGEND_NAMES in item_content and \
                isinstance(item_content[PDFTemplateConstant.PDF_CHART_LEGEND_NAMES], str):
            item_content[PDFTemplateConstant.PDF_CHART_LEGEND_NAMES] = \
                list_eval(item_content[PDFTemplateConstant.PDF_CHART_LEGEND_NAMES])
        if PDFTemplateConstant.PDF_CHART_LEGEND_ADJUST_X in item_content:
            item_content[PDFTemplateConstant.PDF_CHART_LEGEND_ADJUST_X] = \
                int(item_content[PDFTemplateConstant.PDF_CHART_LEGEND_ADJUST_X])
        if PDFTemplateConstant.PDF_CHART_LEGEND_ADJUST_Y in item_content:
            item_content[PDFTemplateConstant.PDF_CHART_LEGEND_ADJUST_Y] = \
                int(item_content[PDFTemplateConstant.PDF_CHART_LEGEND_ADJUST_Y])
        if PDFTemplateConstant.PDF_CHART_STEP_COUNT in item_content:
            item_content[PDFTemplateConstant.PDF_CHART_STEP_COUNT] = \
                int(item_content[PDFTemplateConstant.PDF_CHART_STEP_COUNT])

    @staticmethod
    def args_check(item_content):
        """
        相关参数校验
        :param item_content:
        :return:
        """
        PDFTemplateItem.args_check(item_content)

        if PDFTemplateConstant.PDF_ITEM_DATA not in item_content:
            raise ValueError("bar chart no %s." % PDFTemplateConstant.PDF_ITEM_DATA)
        if item_content[PDFTemplateConstant.PDF_ITEM_DATA] and \
                not isinstance(item_content[PDFTemplateConstant.PDF_ITEM_DATA], list):
            raise ValueError("bar chart %s format error." % PDFTemplateConstant.PDF_ITEM_DATA)
        if PDFTemplateConstant.PDF_CHART_MT_FONT_SIZE in item_content and \
                not isinstance(item_content[PDFTemplateConstant.PDF_CHART_MT_FONT_SIZE], int):
            raise ValueError("bar chart %s format error." % PDFTemplateConstant.PDF_CHART_MT_FONT_SIZE)
        if PDFTemplateConstant.PDF_CHART_MT_FONT_COLOR in item_content and \
                not isinstance(item_content[PDFTemplateConstant.PDF_CHART_MT_FONT_COLOR], Color):
            raise ValueError("bar chart %s format error." % PDFTemplateConstant.PDF_CHART_MT_FONT_COLOR)
        if PDFTemplateConstant.PDF_CHART_CAT_NAMES in item_content and \
                not isinstance(item_content[PDFTemplateConstant.PDF_CHART_CAT_NAMES], list):
            raise ValueError("bar chart %s format error." % PDFTemplateConstant.PDF_CHART_CAT_NAMES)
        if PDFTemplateConstant.PDF_CHART_CAT_LABEL_ANGLE in item_content and \
                not isinstance(item_content[PDFTemplateConstant.PDF_CHART_CAT_LABEL_ANGLE], int):
            raise ValueError("bar chart %s format error." % PDFTemplateConstant.PDF_CHART_CAT_LABEL_ANGLE)
        if PDFTemplateConstant.PDF_CHART_CAT_LABEL_ALL in item_content and \
                not isinstance(item_content[PDFTemplateConstant.PDF_CHART_CAT_LABEL_ALL], bool):
            raise ValueError("bar chart %s format error." % PDFTemplateConstant.PDF_CHART_CAT_LABEL_ALL)
        if PDFTemplateConstant.PDF_CHART_LEGEND_NAMES in item_content and \
                not isinstance(item_content[PDFTemplateConstant.PDF_CHART_LEGEND_NAMES], list):
            raise ValueError("bar chart %s format error." % PDFTemplateConstant.PDF_CHART_LEGEND_NAMES)
        if PDFTemplateConstant.PDF_CHART_LEGEND_ADJUST_X in item_content and \
                not isinstance(item_content[PDFTemplateConstant.PDF_CHART_LEGEND_ADJUST_X], int):
            raise ValueError("bar chart %s format error." % PDFTemplateConstant.PDF_CHART_LEGEND_ADJUST_X)
        if PDFTemplateConstant.PDF_CHART_LEGEND_ADJUST_Y in item_content and \
                not isinstance(item_content[PDFTemplateConstant.PDF_CHART_LEGEND_ADJUST_Y], int):
            raise ValueError("bar chart %s format error." % PDFTemplateConstant.PDF_CHART_LEGEND_ADJUST_Y)
        if PDFTemplateConstant.PDF_CHART_STEP_COUNT in item_content and \
                not isinstance(item_content[PDFTemplateConstant.PDF_CHART_STEP_COUNT], int):
            raise ValueError("bar chart %s format error." % PDFTemplateConstant.PDF_CHART_STEP_COUNT)

    @staticmethod
    def _draw_bar_chart(format_json):
        """
        生成柱状图对象
        :param format_json:
        :return:
        """
        width = format_json[PDFTemplateConstant.PDF_RECT][2]
        height = format_json[PDFTemplateConstant.PDF_RECT][3]

        d = Drawing(width, height, vAlign="TOP")

        if format_json[PDFTemplateConstant.PDF_ITEM_DATA] is None or \
                isinstance(format_json[PDFTemplateConstant.PDF_ITEM_DATA], str):
            PDFTemplateItem._draw_item_rect(d, 20, 20, width - 40, height - 50, format_json)
        elif type(format_json[PDFTemplateConstant.PDF_ITEM_DATA]) is list:
            cat_names = format_json[PDFTemplateConstant.PDF_CHART_CAT_NAMES]
            data = format_json[PDFTemplateConstant.PDF_ITEM_DATA]
            bar_style = format_json[PDFTemplateConstant.PDF_BAR_BAR_STYLE]

            style = "parallel"
            if PDFTemplateConstant.PDF_BAR_STYLE in format_json and \
                    isString(format_json[PDFTemplateConstant.PDF_BAR_STYLE]) is True:
                style = format_json[PDFTemplateConstant.PDF_BAR_STYLE]
            label_format = None
            if PDFTemplateConstant.PDF_BAR_LABEL_FORMAT in format_json and \
                    isString(format_json[PDFTemplateConstant.PDF_BAR_LABEL_FORMAT]) is True:
                label_format = format_json[PDFTemplateConstant.PDF_BAR_LABEL_FORMAT]
            step_count = 4
            if PDFTemplateConstant.PDF_CHART_STEP_COUNT in format_json and \
                    isNumber(format_json[PDFTemplateConstant.PDF_CHART_STEP_COUNT]) is True:
                step_count = format_json[PDFTemplateConstant.PDF_CHART_STEP_COUNT]
            legend_names = None
            if PDFTemplateConstant.PDF_CHART_LEGEND_NAMES in format_json and \
                    isListOfStrings(format_json[PDFTemplateConstant.PDF_CHART_LEGEND_NAMES]) is True:
                legend_names = format_json[PDFTemplateConstant.PDF_CHART_LEGEND_NAMES]
            legend_position = "top-right"
            if PDFTemplateConstant.PDF_CHART_LEGEND_POSITION in format_json and \
                    isString(format_json[PDFTemplateConstant.PDF_CHART_LEGEND_POSITION]) is True:
                legend_position = format_json[PDFTemplateConstant.PDF_CHART_LEGEND_POSITION]
            legend_adjust_x = 0
            if PDFTemplateConstant.PDF_CHART_LEGEND_ADJUST_X in format_json and \
                    isNumber(format_json[PDFTemplateConstant.PDF_CHART_LEGEND_ADJUST_X]) is True:
                legend_adjust_x = format_json[PDFTemplateConstant.PDF_CHART_LEGEND_ADJUST_X]
            legend_adjust_y = 0
            if PDFTemplateConstant.PDF_CHART_LEGEND_ADJUST_Y in format_json and \
                    isNumber(format_json[PDFTemplateConstant.PDF_CHART_LEGEND_ADJUST_Y]) is True:
                legend_adjust_y = format_json[PDFTemplateConstant.PDF_CHART_LEGEND_ADJUST_Y]
            main_title = ""
            if PDFTemplateConstant.PDF_CHART_MAIN_TITLE in format_json and \
                    isString(format_json[PDFTemplateConstant.PDF_CHART_MAIN_TITLE]) is True:
                main_title = format_json[PDFTemplateConstant.PDF_CHART_MAIN_TITLE]
            main_title_font_name = None
            if PDFTemplateConstant.PDF_CHART_MT_FONT_NAME in format_json and \
                    isString(format_json[PDFTemplateConstant.PDF_CHART_MT_FONT_NAME]) is True:
                main_title_font_name = format_json[PDFTemplateConstant.PDF_CHART_MT_FONT_NAME]
            main_title_font_size = None
            if PDFTemplateConstant.PDF_CHART_MT_FONT_SIZE in format_json and \
                    isNumber(format_json[PDFTemplateConstant.PDF_CHART_MT_FONT_SIZE]) is True:
                main_title_font_size = format_json[PDFTemplateConstant.PDF_CHART_MT_FONT_SIZE]
            main_title_font_color = None
            if PDFTemplateConstant.PDF_CHART_MT_FONT_COLOR in format_json:
                main_title_font_color = format_json[PDFTemplateConstant.PDF_CHART_MT_FONT_COLOR]
            x_desc = None
            if PDFTemplateConstant.PDF_CHART_X_DESC in format_json and \
                    isString(format_json[PDFTemplateConstant.PDF_CHART_X_DESC]) is True:
                x_desc = format_json[PDFTemplateConstant.PDF_CHART_X_DESC]
            y_desc = None
            if PDFTemplateConstant.PDF_CHART_Y_DESC in format_json and \
                    isString(format_json[PDFTemplateConstant.PDF_CHART_Y_DESC]) is True:
                y_desc = format_json[PDFTemplateConstant.PDF_CHART_Y_DESC]
            cat_label_all = False
            if PDFTemplateConstant.PDF_CHART_CAT_LABEL_ALL in format_json:
                cat_label_all = format_json[PDFTemplateConstant.PDF_CHART_CAT_LABEL_ALL]
            cat_label_angle = 30
            if PDFTemplateConstant.PDF_CHART_CAT_LABEL_ANGLE in format_json and \
                    isNumber(format_json[PDFTemplateConstant.PDF_CHART_CAT_LABEL_ANGLE]) is True:
                cat_label_angle = format_json[PDFTemplateConstant.PDF_CHART_CAT_LABEL_ANGLE]

            bar_chart = None
            if bar_style == "horizontal":
                bar_chart = ReportLabHorizontalBarChart(
                    0, 0, width, height, cat_names, data, style=style,
                    label_format=label_format, step_count=step_count,
                    legend_names=legend_names, legend_position=legend_position,
                    legend_adjust_x=legend_adjust_x, legend_adjust_y=legend_adjust_y,
                    main_title=main_title, main_title_font_name=main_title_font_name,
                    main_title_font_size=main_title_font_size,
                    main_title_font_color=main_title_font_color, x_desc=x_desc, y_desc=y_desc,
                    cat_label_angle=cat_label_angle, cat_label_all=cat_label_all)
            elif bar_style == "vertical":
                bar_chart = ReportLabVerticalBarChart(
                    0, 0, width, height, cat_names, data, style=style,
                    label_format=label_format, step_count=step_count,
                    legend_names=legend_names, legend_position=legend_position,
                    legend_adjust_x=legend_adjust_x, legend_adjust_y=legend_adjust_y,
                    main_title=main_title, main_title_font_name=main_title_font_name,
                    main_title_font_size=main_title_font_size,
                    main_title_font_color=main_title_font_color, x_desc=x_desc, y_desc=y_desc,
                    cat_label_angle=cat_label_angle, cat_label_all=cat_label_all)
            if bar_chart is not None:
                d.add(bar_chart)

        return d

    def draw(self, cv, show_border=False):
        """
        画柱状图
        :param cv:
        :param show_border:
        :return:
        """
        PDFTemplateItem.draw(self, cv, show_border)

        d = self._draw_bar_chart(self.item_content)

        d.wrapOn(cv, self.item_content[PDFTemplateConstant.PDF_RECT][2],
                 self.item_content[PDFTemplateConstant.PDF_RECT][3])
        d.drawOn(cv, self.item_content[PDFTemplateConstant.PDF_RECT][0],
                 self.item_content[PDFTemplateConstant.PDF_RECT][1])


class PDFTemplatePieChart(PDFTemplateItem):
    """
    饼图
    """

    def __init__(self, item_content):
        PDFTemplateItem.__init__(self, item_content)

    @staticmethod
    def format_content(item_content):
        """
        格式化相关数据
        :param item_content:
        :return:
        """
        PDFTemplateItem.format_content(item_content)

        if PDFTemplateConstant.PDF_ITEM_DATA in item_content and \
                isinstance(item_content[PDFTemplateConstant.PDF_ITEM_DATA], str):
            item_content[PDFTemplateConstant.PDF_ITEM_DATA] = \
                list_eval(item_content[PDFTemplateConstant.PDF_ITEM_DATA])
        if PDFTemplateConstant.PDF_CHART_MT_FONT_SIZE in item_content:
            item_content[PDFTemplateConstant.PDF_CHART_MT_FONT_SIZE] = \
                int(item_content[PDFTemplateConstant.PDF_CHART_MT_FONT_SIZE])
        if PDFTemplateConstant.PDF_CHART_MT_FONT_COLOR in item_content and \
                isinstance(item_content[PDFTemplateConstant.PDF_CHART_MT_FONT_COLOR], str):
            item_content[PDFTemplateConstant.PDF_CHART_MT_FONT_COLOR] = \
                color_eval(item_content[PDFTemplateConstant.PDF_CHART_MT_FONT_COLOR])
        if PDFTemplateConstant.PDF_CHART_LEGEND_NAMES in item_content and \
                isString(item_content[PDFTemplateConstant.PDF_CHART_LEGEND_NAMES]):
            item_content[PDFTemplateConstant.PDF_CHART_LEGEND_NAMES] = \
                list_eval(item_content[PDFTemplateConstant.PDF_CHART_LEGEND_NAMES])

    @staticmethod
    def args_check(item_content):
        """
        相关参数校验
        :param item_content:
        :return:
        """
        PDFTemplateItem.args_check(item_content)

        if PDFTemplateConstant.PDF_ITEM_DATA not in item_content:
            raise ValueError("pie chart no %s." % PDFTemplateConstant.PDF_ITEM_DATA)
        if item_content[PDFTemplateConstant.PDF_ITEM_DATA] and \
                not isinstance(item_content[PDFTemplateConstant.PDF_ITEM_DATA], list):
            raise ValueError("pie chart %s format error." % PDFTemplateConstant.PDF_ITEM_DATA)
        if PDFTemplateConstant.PDF_CHART_MT_FONT_SIZE in item_content and \
                not isinstance(item_content[PDFTemplateConstant.PDF_CHART_MT_FONT_SIZE], int):
            raise ValueError("pie chart %s format error." % PDFTemplateConstant.PDF_CHART_MT_FONT_SIZE)
        if PDFTemplateConstant.PDF_CHART_MT_FONT_COLOR in item_content and \
                not isinstance(item_content[PDFTemplateConstant.PDF_CHART_MT_FONT_COLOR], Color):
            raise ValueError("pie chart %s format error." % PDFTemplateConstant.PDF_CHART_MT_FONT_COLOR)
        if PDFTemplateConstant.PDF_CHART_LEGEND_NAMES in item_content and \
                not isinstance(item_content[PDFTemplateConstant.PDF_CHART_LEGEND_NAMES], list):
            raise ValueError("pie chart %s format error." % PDFTemplateConstant.PDF_CHART_LEGEND_NAMES)

    @staticmethod
    def _draw_pie_chart(format_json):
        """
        生成饼图对象
        :param format_json:
        :return:
        """
        width = format_json[PDFTemplateConstant.PDF_RECT][2]
        height = format_json[PDFTemplateConstant.PDF_RECT][3]

        d = Drawing(width, height, vAlign="TOP")

        if format_json[PDFTemplateConstant.PDF_ITEM_DATA] is None or \
                isString(format_json[PDFTemplateConstant.PDF_ITEM_DATA]):
            PDFTemplateItem._draw_item_rect(d, 20, 20, width - 40, height - 50, format_json)
        elif type(format_json[PDFTemplateConstant.PDF_ITEM_DATA]) is list:
            cat_names = format_json[PDFTemplateConstant.PDF_CHART_CAT_NAMES]
            data = format_json[PDFTemplateConstant.PDF_ITEM_DATA]

            main_title = ""
            if PDFTemplateConstant.PDF_CHART_MAIN_TITLE in format_json and \
                    isString(format_json[PDFTemplateConstant.PDF_CHART_MAIN_TITLE]) is True:
                main_title = format_json[PDFTemplateConstant.PDF_CHART_MAIN_TITLE]
            main_title_font_name = None
            if PDFTemplateConstant.PDF_CHART_MT_FONT_NAME in format_json and \
                    isString(format_json[PDFTemplateConstant.PDF_CHART_MT_FONT_NAME]) is True:
                main_title_font_name = format_json[PDFTemplateConstant.PDF_CHART_MT_FONT_NAME]
            main_title_font_size = None
            if PDFTemplateConstant.PDF_CHART_MT_FONT_SIZE in format_json and \
                    isNumber(format_json[PDFTemplateConstant.PDF_CHART_MT_FONT_SIZE]) is True:
                main_title_font_size = format_json[PDFTemplateConstant.PDF_CHART_MT_FONT_SIZE]
            main_title_font_color = None
            if PDFTemplateConstant.PDF_CHART_MT_FONT_COLOR in format_json:
                main_title_font_color = format_json[PDFTemplateConstant.PDF_CHART_MT_FONT_COLOR]

            pie_chart = ReportLabPieChart(0, 0, width, height, cat_names, data, main_title=main_title,
                                          main_title_font_name=main_title_font_name,
                                          main_title_font_size=main_title_font_size,
                                          main_title_font_color=main_title_font_color,
                                          draw_legend=True)
            d.add(pie_chart)

        return d

    def draw(self, cv, show_border=False):
        """
        画饼图
        :param cv:
        :param show_border:
        :return:
        """
        PDFTemplateItem.draw(self, cv, show_border)

        d = self._draw_pie_chart(self.item_content)

        d.wrapOn(cv, self.item_content[PDFTemplateConstant.PDF_RECT][2],
                 self.item_content[PDFTemplateConstant.PDF_RECT][3])
        d.drawOn(cv, self.item_content[PDFTemplateConstant.PDF_RECT][0],
                 self.item_content[PDFTemplateConstant.PDF_RECT][1])


class PDFTemplateParagraph(PDFTemplateItem):
    """
    文字段落
    """

    paragraph_leading = 1.5

    def __init__(self, item_content):
        PDFTemplateItem.__init__(self, item_content)

    @staticmethod
    def format_content(item_content):
        """
        格式化相关数据
        :param item_content:
        :return:
        """
        PDFTemplateItem.format_content(item_content)

        if PDFTemplateConstant.PDF_ITEM_CONTENT in item_content and \
                item_content[PDFTemplateConstant.PDF_ITEM_CONTENT] is None:
            item_content[PDFTemplateConstant.PDF_ITEM_CONTENT] = ""
        if PDFTemplateConstant.PDF_PARAGRAPH_STYLE not in item_content:
            item_content[PDFTemplateConstant.PDF_PARAGRAPH_STYLE] = "BodyText"
        if PDFTemplateConstant.PDF_FONT_SIZE in item_content:
            item_content[PDFTemplateConstant.PDF_FONT_SIZE] = int(item_content[PDFTemplateConstant.PDF_FONT_SIZE])
        if PDFTemplateConstant.PDF_FONT_COLOR in item_content and \
                isinstance(item_content[PDFTemplateConstant.PDF_FONT_COLOR], str):
            item_content[PDFTemplateConstant.PDF_FONT_COLOR] = \
                color_eval(item_content[PDFTemplateConstant.PDF_FONT_COLOR])
        if PDFTemplateConstant.PDF_PARAGRAPH_INDENT in item_content:
            item_content[PDFTemplateConstant.PDF_PARAGRAPH_INDENT] = \
                int(item_content[PDFTemplateConstant.PDF_PARAGRAPH_INDENT])

    @staticmethod
    def args_check(item_content):
        """
        相关参数校验
        :param item_content:
        :return:
        """
        PDFTemplateItem.args_check(item_content)

        if PDFTemplateConstant.PDF_ITEM_CONTENT not in item_content:
            raise ValueError("paragraph no %s." % PDFTemplateConstant.PDF_ITEM_CONTENT)
        if PDFTemplateConstant.PDF_FONT_SIZE in item_content and \
                not isinstance(item_content[PDFTemplateConstant.PDF_FONT_SIZE], int):
            raise ValueError("paragraph %s format error." % PDFTemplateConstant.PDF_FONT_SIZE)
        if PDFTemplateConstant.PDF_FONT_COLOR in item_content and \
                not isinstance(item_content[PDFTemplateConstant.PDF_FONT_COLOR], Color):
            raise ValueError("paragraph %s format error." % PDFTemplateConstant.PDF_FONT_COLOR)
        if PDFTemplateConstant.PDF_PARAGRAPH_INDENT in item_content and \
                not isinstance(item_content[PDFTemplateConstant.PDF_PARAGRAPH_INDENT], int):
            raise ValueError("paragraph %s format error." % PDFTemplateConstant.PDF_PARAGRAPH_INDENT)

    @staticmethod
    def _draw_paragraph(format_json):
        """
        生成段落对象
        :param format_json:
        :return:
        """
        content = format_json[PDFTemplateConstant.PDF_ITEM_CONTENT]
        style_name = format_json[PDFTemplateConstant.PDF_PARAGRAPH_STYLE]
        font_name = DefaultFontName
        if PDFTemplateConstant.PDF_FONT_NAME in format_json:
            font_name = format_json[PDFTemplateConstant.PDF_FONT_NAME]
        font_color = None
        if PDFTemplateConstant.PDF_FONT_COLOR in format_json:
            font_color = format_json[PDFTemplateConstant.PDF_FONT_COLOR]
        font_size = None
        if PDFTemplateConstant.PDF_FONT_SIZE in format_json:
            font_size = format_json[PDFTemplateConstant.PDF_FONT_SIZE]
        indent_flag = 0
        if PDFTemplateConstant.PDF_PARAGRAPH_INDENT in format_json:
            indent_flag = format_json[PDFTemplateConstant.PDF_PARAGRAPH_INDENT]

        stylesheet = getSampleStyleSheet()
        ss = stylesheet[style_name]
        ss.fontName = font_name
        if font_size:
            ss.fontSize = font_size
        if font_color:
            ss.fillColor = font_color
        word_width = stringWidth(" ", ss.fontName, ss.fontSize) * 2
        ss.leading = word_width * PDFTemplateParagraph.paragraph_leading
        if indent_flag:
            ss.firstLineIndent = word_width * 2

        paragraph = Paragraph(content, ss)
        if "force_top" in format_json and int(format_json['force_top']) == 1:
            _, h = paragraph.wrap(format_json[PDFTemplateConstant.PDF_RECT][2],
                                  format_json[PDFTemplateConstant.PDF_RECT][3])
            format_json[PDFTemplateConstant.PDF_RECT][1] = \
                format_json[PDFTemplateConstant.PDF_RECT][1] + format_json[PDFTemplateConstant.PDF_RECT][3] - h

        return paragraph

    @staticmethod
    def _calc_paragraph_height(item):
        """
        获取段落高度
        :param item:
        :return:
        """
        p = PDFTemplateParagraph._draw_paragraph(item)
        _, h = p.wrap(item[PDFTemplateConstant.PDF_RECT][2], 0)
        del p
        return h

    @staticmethod
    def auto_set_height(item):
        """
        自动设置高度
        :param item:
        :return:
        """
        item[PDFTemplateConstant.PDF_RECT][3] = PDFTemplateParagraph._calc_paragraph_height(item)

    @staticmethod
    def _split_paragraph_text_by_height(item, split_height):
        """
        按照高度切分出段落文字
        :param item:
        :param split_height:
        :return:
        """
        content = item[PDFTemplateConstant.PDF_ITEM_CONTENT]
        str_len = len(content)
        content_height = PDFTemplateParagraph._calc_paragraph_height(item)
        split_index = int(split_height / content_height * str_len)

        tmp_item = deepcopy(item)
        tmp_item[PDFTemplateConstant.PDF_ITEM_CONTENT] = content[:split_index]
        content_height = PDFTemplateParagraph._calc_paragraph_height(tmp_item)

        if content_height > split_height:
            flag = 0
        else:
            flag = 1

        while split_index > 0 or split_index < str_len:
            if flag == 0:
                split_index -= 1
            else:
                split_index += 1

            tmp_item[PDFTemplateConstant.PDF_ITEM_CONTENT] = content[:split_index]
            tmp_height = PDFTemplateParagraph._calc_paragraph_height(tmp_item)

            if flag == 0:
                if tmp_height <= split_height:
                    split_index -= 1
                    break
            else:
                if tmp_height >= split_height:
                    split_index -= 1
                    break
        del tmp_item

        return split_index

    @staticmethod
    def split_by_height(items, index, page_height):
        """
        按照高度进行分割
        :param items:
        :param index:
        :param page_height:
        :return:
        """
        item = items[index]
        if item[PDFTemplateConstant.PDF_ITEM_TYPE] != PDFTemplateConstant.PDF_ITEM_TYPE_PARAGRAPH:
            return False

        item_height = item[PDFTemplateConstant.PDF_RECT][3]
        y = item[PDFTemplateConstant.PDF_RECT][1]
        if item_height + y <= page_height:
            return True

        split_height = page_height - y
        split_index = PDFTemplateParagraph._split_paragraph_text_by_height(item, split_height)

        new_item = deepcopy(item)
        new_item[PDFTemplateConstant.PDF_ITEM_CONTENT] = new_item[PDFTemplateConstant.PDF_ITEM_CONTENT][split_index:]
        new_item[PDFTemplateConstant.PDF_PARAGRAPH_INDENT] = 0

        item[PDFTemplateConstant.PDF_ITEM_CONTENT] = item[PDFTemplateConstant.PDF_ITEM_CONTENT][:split_index]
        item[PDFTemplateConstant.PDF_RECT][3] = split_height

        items.insert(index + 1, new_item)

        return True

    def draw(self, cv, show_border=False):
        """
        画段落
        :param cv:
        :param show_border:
        :return:
        """
        PDFTemplateItem.draw(self, cv, show_border)

        d = self._draw_paragraph(self.item_content)

        d.wrapOn(cv, self.item_content[PDFTemplateConstant.PDF_RECT][2],
                 self.item_content[PDFTemplateConstant.PDF_RECT][3])
        d.drawOn(cv, self.item_content[PDFTemplateConstant.PDF_RECT][0],
                 self.item_content[PDFTemplateConstant.PDF_RECT][1])


class PDFTemplateText(PDFTemplateItem):
    """
    文字Text
    """

    def __init__(self, item_content):
        PDFTemplateItem.__init__(self, item_content)

    @staticmethod
    def format_content(item_content):
        """
        格式化相关数据
        :param item_content:
        :return:
        """
        PDFTemplateItem.format_content(item_content)

        if PDFTemplateConstant.PDF_FONT_SIZE in item_content:
            item_content[PDFTemplateConstant.PDF_FONT_SIZE] = \
                int(item_content[PDFTemplateConstant.PDF_FONT_SIZE])
        if PDFTemplateConstant.PDF_FONT_COLOR in item_content and \
                isinstance(item_content[PDFTemplateConstant.PDF_FONT_COLOR], str):
            item_content[PDFTemplateConstant.PDF_FONT_COLOR] = \
                color_eval(item_content[PDFTemplateConstant.PDF_FONT_COLOR])

    @staticmethod
    def args_check(item_content):
        """
        相关参数校验
        :param item_content:
        :return:
        """
        PDFTemplateItem.args_check(item_content)

        if PDFTemplateConstant.PDF_ITEM_CONTENT not in item_content:
            raise ValueError("text no %s." % PDFTemplateConstant.PDF_ITEM_CONTENT)
        if PDFTemplateConstant.PDF_FONT_SIZE in item_content and \
                not isinstance(item_content[PDFTemplateConstant.PDF_FONT_SIZE], int):
            raise ValueError("text %s format error." % PDFTemplateConstant.PDF_FONT_SIZE)
        if PDFTemplateConstant.PDF_FONT_COLOR in item_content and \
                not isinstance(item_content[PDFTemplateConstant.PDF_FONT_COLOR], Color):
            raise ValueError("text %s format error." % PDFTemplateConstant.PDF_FONT_COLOR)

    def draw(self, cv, show_border=False):
        """
        画Text
        :param cv:
        :param show_border:
        :return:
        """
        PDFTemplateItem.draw(self, cv, show_border)

        d = self._draw_text(self.item_content)

        d.wrapOn(cv, self.item_content[PDFTemplateConstant.PDF_RECT][2],
                 self.item_content[PDFTemplateConstant.PDF_RECT][3])
        d.drawOn(cv, self.item_content[PDFTemplateConstant.PDF_RECT][0],
                 self.item_content[PDFTemplateConstant.PDF_RECT][1])


class PDFTemplateTable(PDFTemplateItem):
    """
    表格
    """

    def __init__(self, item_content):
        PDFTemplateItem.__init__(self, item_content)

    @staticmethod
    def format_content(item_content):
        """
        格式化相关数据
        :param item_content:
        :return:
        """
        PDFTemplateItem.format_content(item_content)

        if PDFTemplateConstant.PDF_TABLE_COLUMNS not in item_content:
            item_content[PDFTemplateConstant.PDF_TABLE_COLUMNS] = []
        elif isinstance(item_content[PDFTemplateConstant.PDF_TABLE_COLUMNS], str):
            item_content[PDFTemplateConstant.PDF_TABLE_COLUMNS] = \
                list_eval(item_content[PDFTemplateConstant.PDF_TABLE_COLUMNS])

        if PDFTemplateConstant.PDF_ITEM_CONTENT not in item_content:
            item_content[PDFTemplateConstant.PDF_ITEM_CONTENT] = []
        elif isinstance(item_content[PDFTemplateConstant.PDF_ITEM_CONTENT], str):
            item_content[PDFTemplateConstant.PDF_ITEM_CONTENT] = \
                list_eval(item_content[PDFTemplateConstant.PDF_ITEM_CONTENT])

        if PDFTemplateConstant.PDF_FONT_SIZE in item_content:
            item_content[PDFTemplateConstant.PDF_FONT_SIZE] = int(item_content[PDFTemplateConstant.PDF_FONT_SIZE])
        if PDFTemplateConstant.PDF_FONT_COLOR in item_content:
            item_content[PDFTemplateConstant.PDF_FONT_COLOR] = \
                color_eval(item_content[PDFTemplateConstant.PDF_FONT_COLOR])

        if PDFTemplateConstant.PDF_TABLE_COL_WIDTHS in item_content:
            if isinstance(item_content[PDFTemplateConstant.PDF_TABLE_COL_WIDTHS], str):
                item_content[PDFTemplateConstant.PDF_TABLE_COL_WIDTHS] = \
                    list_eval(item_content[PDFTemplateConstant.PDF_TABLE_COL_WIDTHS])
                for i in range(len(item_content[PDFTemplateConstant.PDF_TABLE_COL_WIDTHS])):
                    if isinstance(item_content[PDFTemplateConstant.PDF_TABLE_COL_WIDTHS][i], str) and \
                            item_content[PDFTemplateConstant.PDF_TABLE_COL_WIDTHS][i].find("%") > 0:
                        item_content[PDFTemplateConstant.PDF_TABLE_COL_WIDTHS][i] = \
                            int(item_content[PDFTemplateConstant.PDF_TABLE_COL_WIDTHS][i].replace("%", ""))
                        item_content[PDFTemplateConstant.PDF_TABLE_COL_WIDTHS][i] = \
                            int(item_content[PDFTemplateConstant.PDF_TABLE_COL_WIDTHS][i] / 100 *
                                item_content[PDFTemplateConstant.PDF_RECT][2])
        else:
            item_content[PDFTemplateConstant.PDF_TABLE_COL_WIDTHS] = []
            col_count = len(item_content[PDFTemplateConstant.PDF_TABLE_COLUMNS])
            for i in range(col_count):
                item_content[PDFTemplateConstant.PDF_TABLE_COL_WIDTHS].append(
                    int(item_content[PDFTemplateConstant.PDF_RECT][2] / col_count)
                )

    @staticmethod
    def args_check(item_content):
        """
        相关参数校验
        :param item_content:
        :return:
        """
        PDFTemplateItem.args_check(item_content)

        if PDFTemplateConstant.PDF_TABLE_COLUMNS not in item_content:
            raise ValueError("don't have %s information." % PDFTemplateConstant.PDF_TABLE_COLUMNS)
        if PDFTemplateConstant.PDF_ITEM_CONTENT not in item_content:
            raise ValueError("don't have %s information." % PDFTemplateConstant.PDF_ITEM_CONTENT)

        if item_content[PDFTemplateConstant.PDF_TABLE_COLUMNS] and \
                isListOfStrings(item_content[PDFTemplateConstant.PDF_TABLE_COLUMNS]) is False:
            raise ValueError("table %s format error." % PDFTemplateConstant.PDF_TABLE_COLUMNS)
        if not isinstance(item_content[PDFTemplateConstant.PDF_ITEM_CONTENT], list):
            raise ValueError("table %s format error." % PDFTemplateConstant.PDF_ITEM_CONTENT)

        if PDFTemplateConstant.PDF_TABLE_COL_WIDTHS in item_content and \
                isListOfNumbers(item_content[PDFTemplateConstant.PDF_TABLE_COL_WIDTHS]) is False:
            raise ValueError("table %s format error." % PDFTemplateConstant.PDF_TABLE_COL_WIDTHS)

    @staticmethod
    def _calc_table_height(item):
        """
        获取表格高度
        :param item:
        :return:
        """
        t = PDFTemplateTable._draw_table(item)
        _, h = t.wrap(1, 1)
        del t
        return h

    @staticmethod
    def auto_set_height(item):
        """
        自动计算表格高度
        :param item:
        :return:
        """
        item[PDFTemplateConstant.PDF_RECT][3] = PDFTemplateTable._calc_table_height(item)

    @staticmethod
    def _cut_table_rows(item, split_height):
        """
        计算分割的行数
        :param item:
        :param split_height:
        :return:
        """
        ret = 0
        t = PDFTemplateTable._draw_table(item)
        t.wrap(1, 1)

        curr_y = 0
        for idx, val in enumerate(t._rowHeights):
            curr_y += val
            if curr_y >= split_height:
                ret = idx
                break

        del t
        return ret - 1

    @staticmethod
    def split_by_height(items, index, page_height):
        """
        按照高度进行分割
        :param items:
        :param index:
        :param page_height:
        :return:
        """
        item = items[index]

        item_height = item[PDFTemplateConstant.PDF_RECT][3]
        y = item[PDFTemplateConstant.PDF_RECT][1]
        if item_height + y <= page_height:
            return True

        split_height = page_height - y
        split_index = PDFTemplateTable._cut_table_rows(item, split_height)

        new_item = deepcopy(item)
        new_item[PDFTemplateConstant.PDF_ITEM_CONTENT] = new_item[PDFTemplateConstant.PDF_ITEM_CONTENT][split_index:]

        item[PDFTemplateConstant.PDF_ITEM_CONTENT] = item[PDFTemplateConstant.PDF_ITEM_CONTENT][:split_index]
        item[PDFTemplateConstant.PDF_RECT][3] = split_height

        items.insert(index + 1, new_item)

        return True

    @staticmethod
    def _draw_table(format_json):
        """
        生成表格对象
        :param format_json:
        :return:
        """
        cols = format_json[PDFTemplateConstant.PDF_TABLE_COLUMNS]
        content = format_json[PDFTemplateConstant.PDF_ITEM_CONTENT]
        table_width = format_json[PDFTemplateConstant.PDF_RECT][2]

        font_name = DefaultFontName
        if PDFTemplateConstant.PDF_FONT_NAME in format_json:
            font_name = format_json[PDFTemplateConstant.PDF_FONT_NAME]
        font_size = STATE_DEFAULTS['fontSize']
        if PDFTemplateConstant.PDF_FONT_SIZE in format_json:
            font_size = format_json[PDFTemplateConstant.PDF_FONT_SIZE]
        font_color = STATE_DEFAULTS['fontSize']
        if PDFTemplateConstant.PDF_FONT_COLOR in format_json:
            font_color = format_json[PDFTemplateConstant.PDF_FONT_COLOR]

        col_widths = [int(table_width / len(cols)) for _ in cols]
        if PDFTemplateConstant.PDF_TABLE_COL_WIDTHS in format_json:
            col_widths = format_json[PDFTemplateConstant.PDF_TABLE_COL_WIDTHS]

        stylesheet = getSampleStyleSheet()
        ss = stylesheet['BodyText']
        ss.fontName = font_name
        ss.fontColor = font_color
        ss.fontSize = font_size

        # convert data to paragraph
        temp = []
        for d in content:
            temp.append(tuple([Paragraph(str(i), ss) for i in d]))
        content = temp

        data = [tuple(cols)]
        data.extend(content)

        # generate table style
        ts = TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), DefaultFontName),
            ('BACKGROUND', (0, 0), (-1, 0), colors.burlywood),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.red),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ])

        # merage data
        table = Table(data, colWidths=col_widths)
        table.setStyle(ts)

        return table

    def draw(self, cv, show_border=False):
        """
        画表格
        :param cv:
        :param show_border:
        :return:
        """
        PDFTemplateItem.draw(self, cv, show_border)

        d = self._draw_table(self.item_content)

        d.wrapOn(cv, self.item_content[PDFTemplateConstant.PDF_RECT][2],
                 self.item_content[PDFTemplateConstant.PDF_RECT][3])
        d.drawOn(cv, self.item_content[PDFTemplateConstant.PDF_RECT][0],
                 self.item_content[PDFTemplateConstant.PDF_RECT][1])


class PDFTemplatePage(object):
    """
    此类负责组织Page中的各Item。
    """

    # 各Item对应的类
    ItemClass = {
        PDFTemplateConstant.PDF_ITEM_TYPE_LINE_CHART: PDFTemplateLineChart,
        PDFTemplateConstant.PDF_ITEM_TYPE_BAR_CHART: PDFTemplateBarChart,
        PDFTemplateConstant.PDF_ITEM_TYPE_PIE_CHART: PDFTemplatePieChart,
        PDFTemplateConstant.PDF_ITEM_TYPE_PARAGRAPH: PDFTemplateParagraph,
        PDFTemplateConstant.PDF_ITEM_TYPE_TEXT: PDFTemplateText,
        PDFTemplateConstant.PDF_ITEM_TYPE_TABLE: PDFTemplateTable
    }

    def __init__(self, page_content, page_num, page_size, **kw):
        self.items = []
        self.page_content = deepcopy(page_content)
        if not isinstance(page_num, int):
            raise ValueError("page number is not int.")
        self.page_num = page_num
        if not isListOfNumbers(page_size):
            raise ValueError("page size is not a list of numbers.")
        self.page_size = page_size
        self.rect = None
        self.coordinate = "left-top"
        self.auto_position = False
        self.x_padding = 0
        self.y_padding = 0
        self.align_type = "middle"
        self.header_text = None

        for k, v in kw.items():
            setattr(self, k, v)

        self.format_content(self.page_content)
        self.args_check(self.page_content)

        if PDFTemplateConstant.PDF_RECT in self.page_content:
            self.rect = self.page_content[PDFTemplateConstant.PDF_RECT]
        if PDFTemplateConstant.PDF_COORDINATE in self.page_content:
            self.coordinate = self.page_content[PDFTemplateConstant.PDF_COORDINATE]
        if PDFTemplateConstant.PDF_AUTO_POSITION in self.page_content:
            self.auto_position = self.page_content[PDFTemplateConstant.PDF_AUTO_POSITION]
        if PDFTemplateConstant.PDF_PAGE_PADDING_X in self.page_content:
            self.x_padding = self.page_content[PDFTemplateConstant.PDF_PAGE_PADDING_X]
        if PDFTemplateConstant.PDF_PAGE_PADDING_Y in self.page_content:
            self.y_padding = self.page_content[PDFTemplateConstant.PDF_PAGE_PADDING_Y]
        if PDFTemplateConstant.PDF_ALIGN_TYPE in self.page_content:
            self.align_type = self.page_content[PDFTemplateConstant.PDF_ALIGN_TYPE]

        for item in self.page_content[PDFTemplateConstant.PDF_ITEMS]:
            self.add_item(item)

    @staticmethod
    def format_content(page_content):
        """
        格式化Page数据
        :param page_content:
        :return:
        """
        if PDFTemplateConstant.PDF_RECT in page_content and \
                isinstance(page_content[PDFTemplateConstant.PDF_RECT], str):
            page_content[PDFTemplateConstant.PDF_RECT] = list_eval(page_content[PDFTemplateConstant.PDF_RECT])

        if PDFTemplateConstant.PDF_AUTO_POSITION not in page_content:
            page_content[PDFTemplateConstant.PDF_AUTO_POSITION] = False
        elif not isinstance(page_content[PDFTemplateConstant.PDF_AUTO_POSITION], bool):
            if page_content[PDFTemplateConstant.PDF_AUTO_POSITION] == "True":
                page_content[PDFTemplateConstant.PDF_AUTO_POSITION] = True
            elif page_content[PDFTemplateConstant.PDF_AUTO_POSITION] == "False":
                page_content[PDFTemplateConstant.PDF_AUTO_POSITION] = False
            else:
                page_content[PDFTemplateConstant.PDF_AUTO_POSITION] = False

        if PDFTemplateConstant.PDF_PAGE_PADDING_X in page_content:
            page_content[PDFTemplateConstant.PDF_PAGE_PADDING_X] = \
                int(page_content[PDFTemplateConstant.PDF_PAGE_PADDING_X])
        else:
            page_content[PDFTemplateConstant.PDF_PAGE_PADDING_X] = 0

        if PDFTemplateConstant.PDF_PAGE_PADDING_Y in page_content:
            page_content[PDFTemplateConstant.PDF_PAGE_PADDING_Y] = \
                int(page_content[PDFTemplateConstant.PDF_PAGE_PADDING_Y])
        else:
            page_content[PDFTemplateConstant.PDF_PAGE_PADDING_Y] = 0

        if PDFTemplateConstant.PDF_ALIGN_TYPE not in page_content:
            page_content[PDFTemplateConstant.PDF_ALIGN_TYPE] = "middle"

        if PDFTemplateConstant.PDF_INVALID not in page_content:
            page_content[PDFTemplateConstant.PDF_INVALID] = False
        elif not isinstance(page_content[PDFTemplateConstant.PDF_INVALID], bool):
            if page_content[PDFTemplateConstant.PDF_INVALID] == "True":
                page_content[PDFTemplateConstant.PDF_INVALID] = True
            elif page_content[PDFTemplateConstant.PDF_INVALID] == "False":
                page_content[PDFTemplateConstant.PDF_INVALID] = False
            else:
                page_content[PDFTemplateConstant.PDF_INVALID] = False

        # 格式化各Item数据
        if PDFTemplateConstant.PDF_ITEMS in page_content:
            for item in page_content[PDFTemplateConstant.PDF_ITEMS]:
                if not isinstance(item, dict):
                    item = page_content[PDFTemplateConstant.PDF_ITEMS][item]
                item_type = item[PDFTemplateConstant.PDF_ITEM_TYPE]

                PDFTemplatePage.ItemClass[item_type].format_content(item)

    @staticmethod
    def args_check(page_content):
        """
        Page数据合法性校验
        :param page_content:
        :return:
        """
        if PDFTemplateConstant.PDF_RECT not in page_content:
            raise ValueError("page no %s." % PDFTemplateConstant.PDF_RECT)

        if not isListOfNumbers(page_content[PDFTemplateConstant.PDF_RECT]) or \
                len(page_content[PDFTemplateConstant.PDF_RECT]) != 4:
            raise ValueError("page %s error." % PDFTemplateConstant.PDF_RECT)

        if PDFTemplateConstant.PDF_ITEMS not in page_content:
            raise ValueError("page no %s." % PDFTemplateConstant.PDF_ITEMS)

        # 各Item数据合法性校验
        for item in page_content[PDFTemplateConstant.PDF_ITEMS]:
            if not isinstance(item, dict):
                item = page_content[PDFTemplateConstant.PDF_ITEMS][item]
            item_type = item[PDFTemplateConstant.PDF_ITEM_TYPE]

            PDFTemplatePage.ItemClass[item_type].args_check(item)

    def add_item(self, item_content):
        """
        往当前页中添加Item
        :param item_content:
        :return:
        """
        if not isinstance(item_content, dict):
            raise ValueError("item format is error.")
        if PDFTemplateConstant.PDF_ITEM_TYPE not in item_content:
            raise ValueError("item has not property: %s." % PDFTemplateConstant.PDF_ITEM_TYPE)

        # 生成Item实例化对象
        item_ins = self.ItemClass[item_content[PDFTemplateConstant.PDF_ITEM_TYPE]](item_content)
        self.items.append(item_ins)

    @staticmethod
    def _calc_position_align(page, page_width, x_padding, start_index, end_index, align_type):
        """
        对每一行的所有Item进行对齐
        :param page:
        :param page_width:
        :param x_padding:
        :param start_index:
        :param end_index:
        :param align_type:
        :return:
        """
        if align_type == "middle" or align_type == "right":
            # 居中、右对齐
            items_width = (end_index - start_index - 1) * x_padding
            for i in range(end_index - start_index):
                item = page[PDFTemplateConstant.PDF_ITEMS][start_index + i]

                margin_left = item[PDFTemplateConstant.PDF_ITEM_MARGIN_LEFT]
                margin_right = item[PDFTemplateConstant.PDF_ITEM_MARGIN_RIGHT]
                items_width += item[PDFTemplateConstant.PDF_RECT][2] + margin_left + margin_right

            start_pos = 0
            if align_type == "middle":
                start_pos = int((page_width - items_width) / 2)
            elif align_type == "right":
                start_pos = page_width - items_width

            for i in range(end_index - start_index):
                item = page[PDFTemplateConstant.PDF_ITEMS][start_index + i]

                margin_left = item[PDFTemplateConstant.PDF_ITEM_MARGIN_LEFT]
                margin_right = item[PDFTemplateConstant.PDF_ITEM_MARGIN_RIGHT]
                item[PDFTemplateConstant.PDF_RECT][0] = start_pos + margin_left
                start_pos += item[PDFTemplateConstant.PDF_RECT][2] + x_padding + margin_left + margin_right
        elif align_type == "left":
            # 默认是左对齐，不用处理
            pass

    @staticmethod
    def calc_position(page):
        """
        自动计算page中的所有Item的位置
        :param page:
        :return:
        """
        next_page = deepcopy(page)
        next_page[PDFTemplateConstant.PDF_ITEMS] = []

        page_width = page[PDFTemplateConstant.PDF_RECT][2]
        page_height = page[PDFTemplateConstant.PDF_RECT][3]
        x_padding = page[PDFTemplateConstant.PDF_PAGE_PADDING_X]
        y_padding = page[PDFTemplateConstant.PDF_PAGE_PADDING_Y]
        align_type = page[PDFTemplateConstant.PDF_ALIGN_TYPE]

        cur_x = 0
        cur_y = 0
        next_y = 0
        next_page_flag = False
        index = 0
        next_page_index = 0
        row_start = 0

        for item in page[PDFTemplateConstant.PDF_ITEMS]:
            item_type = item[PDFTemplateConstant.PDF_ITEM_TYPE]

            # 自动计算Item的高度
            PDFTemplatePage.ItemClass[item_type].auto_set_height(item)

            item_width = item[PDFTemplateConstant.PDF_RECT][2]
            item_height = item[PDFTemplateConstant.PDF_RECT][3]

            margin_left = item[PDFTemplateConstant.PDF_ITEM_MARGIN_LEFT]
            margin_right = item[PDFTemplateConstant.PDF_ITEM_MARGIN_RIGHT]
            margin_top = item[PDFTemplateConstant.PDF_ITEM_MARGIN_TOP]
            margin_bottom = item[PDFTemplateConstant.PDF_ITEM_MARGIN_BOTTOM]

            if cur_x != 0 and cur_x + item_width + margin_left + margin_right > page_width:
                # 需要换行显示

                # 对本行中的Item进行对齐
                PDFTemplatePage._calc_position_align(page, page_width, x_padding, row_start, index, align_type)

                next_page_index = index
                row_start = index
                item[PDFTemplateConstant.PDF_RECT][0] = margin_left
                item[PDFTemplateConstant.PDF_RECT][1] = next_y + margin_top
                cur_x = item_width + x_padding + margin_left + margin_right
                cur_y = next_y
                next_y = cur_y + item_height + y_padding + margin_top + margin_bottom
            else:
                # 不需要换行，从左到右依次放置

                item[PDFTemplateConstant.PDF_RECT][0] = cur_x + margin_left
                item[PDFTemplateConstant.PDF_RECT][1] = cur_y + margin_top
                cur_x += item_width + x_padding + margin_left + margin_right
                if cur_y + item_height + y_padding + margin_top + margin_bottom > next_y:
                    next_y = cur_y + item_height + y_padding + margin_top + margin_bottom

            if next_y > page_height:
                # 需要分页显示

                # 尝试对当前Item进行拆分
                split_flag = PDFTemplatePage.ItemClass[item_type].split_by_height(
                    page[PDFTemplateConstant.PDF_ITEMS], index, page_height
                )
                if split_flag:
                    # 拆分成功
                    next_page_index += 1
                    index += 1
                if split_flag or cur_y != 0:
                    # 拆分成功，或者当前Item不是当前页中的第一个，则跳出循环，剩下的Item移到下一页处理
                    next_page_flag = True
                    break

            index += 1
        # 处理最后一行的对齐
        PDFTemplatePage._calc_position_align(page, page_width, x_padding, row_start, index, align_type)

        if next_page_flag:
            # 取出需要放到下一页的Item，并返回
            next_page[PDFTemplateConstant.PDF_ITEMS] = page[PDFTemplateConstant.PDF_ITEMS][next_page_index:]
            page[PDFTemplateConstant.PDF_ITEMS] = page[PDFTemplateConstant.PDF_ITEMS][:next_page_index]
            return next_page

        return None

    def _compute_coord(self):
        """
        坐标计算（转换）
        :return:
        """
        for item_ins in self.items:
            x, y, _, h = item_ins.get_rect()
            x = x + self.rect[0]
            y = y + self.rect[1]
            if self.coordinate == "left-top":
                y = self.page_size[1] - y - h

            item_ins.set_rect(x=x, y=y)

    def _draw_header(self, cv):
        """
        画页眉
        :param cv:
        :return:
        """
        start_x = int(self.page_size[0] / 10)

        width = self.page_size[0]
        height = int(self.page_size[1] / 15)

        d = Drawing(width, height, vAlign="TOP")

        header_line = Line(start_x, 0, width - start_x, 0)
        d.add(header_line)

        if self.header_text:
            x = int(width / 2)
            y = 5

            text = String(x, y, self.header_text)
            text.fontName = DefaultFontName
            text.textAnchor = "middle"

            d.add(text)

        d.wrapOn(cv, width, height)
        d.drawOn(cv, 0, self.page_size[1] - height)

    def _draw_feet(self, cv):
        """
        画页脚
        :param cv:
        :return:
        """
        start_x = int(self.page_size[0] / 10)

        width = self.page_size[0]
        height = int(self.page_size[1] / 15)

        d = Drawing(width, height, vAlign="TOP")

        feet_line = Line(start_x, height, width - start_x, height)
        d.add(feet_line)

        if self.page_num is not None:
            x = int(width / 2)
            y = height - STATE_DEFAULTS['fontSize']

            text = String(x, y, str(self.page_num + 1))
            text.fontName = DefaultFontName
            text.textAnchor = "middle"

            d.add(text)

        d.wrapOn(cv, width, height)
        d.drawOn(cv, 0, 0)

    def draw(self, cv, show_border=False):
        """
        画Page
        :param cv:
        :param show_border:
        :return:
        """
        self._compute_coord()

        # 画页眉
        self._draw_header(cv)
        # 画页脚
        self._draw_feet(cv)

        # 画Page中的各Item
        for item_ins in self.items:
            item_ins.draw(cv, show_border)

        # 画Page边界
        if show_border:
            PDFTemplateItem.draw_border(cv, self.rect[0], self.rect[1], self.rect[2], self.rect[3],
                                        Color(0, 0, 1, 1), 2)


class PDFTemplateR(object):
    """
    此类负责处理读取模板文件，组织文件中的各Page。
    """

    def __init__(self, template_file):
        self._template_file = template_file

        self._template_content = None
        self._pages = None
        self._valid_pages = None
        self._pdf_file = None
        self._author = None
        self._title = None
        self._page_size = None
        self._coordinate = "left-top"
        self._header_text = None
        self._show_border = False
        self._cv = None

        self._read_template_file()

    def _read_template_file(self):
        """
        读取模板文件，并对内容进行格式化，以及参数校验。
        :return:
        """
        try:
            with open(self._template_file, "r", encoding='UTF-8') as f:
                template = f.read()

            template = xmltodict.parse(template)['pdf']

            if PDFTemplateConstant.PDF_PAGES not in template:
                raise ValueError("template no %s." % PDFTemplateConstant.PDF_PAGES)
            if PDFTemplateConstant.PDF_FILE_NAME not in template:
                raise ValueError("template no %s." % PDFTemplateConstant.PDF_FILE_NAME)
            if PDFTemplateConstant.PDF_PAGE_SIZE not in template:
                raise ValueError("template no %s." % PDFTemplateConstant.PDF_PAGE_SIZE)

            template[PDFTemplateConstant.PDF_PAGE_SIZE] = list_eval(template[PDFTemplateConstant.PDF_PAGE_SIZE])
            if PDFTemplateConstant.PDF_SHOW_BORDER in template:
                template[PDFTemplateConstant.PDF_SHOW_BORDER] = \
                    bool_eval(template[PDFTemplateConstant.PDF_SHOW_BORDER])
            else:
                template[PDFTemplateConstant.PDF_SHOW_BORDER] = False

            for page in template[PDFTemplateConstant.PDF_PAGES]:
                page = template[PDFTemplateConstant.PDF_PAGES][page]
                # 格式化Page数据
                PDFTemplatePage.format_content(page)
                # 各参数合法性校验
                PDFTemplatePage.args_check(page)
        except Exception as err_info:
            import traceback
            traceback.print_exc()
            print(err_info)
            raise ValueError("PDF template file format error.")

        self._template_content = template
        self._pages = self._template_content[PDFTemplateConstant.PDF_PAGES]
        self._pdf_file = self._template_content[PDFTemplateConstant.PDF_FILE_NAME]
        self._page_size = self._template_content[PDFTemplateConstant.PDF_PAGE_SIZE]

        if PDFTemplateConstant.PDF_AUTHOR in self._template_content:
            self._author = self._template_content[PDFTemplateConstant.PDF_AUTHOR]
        if PDFTemplateConstant.PDF_TITLE in self._template_content:
            self._title = self._template_content[PDFTemplateConstant.PDF_TITLE]
        if PDFTemplateConstant.PDF_COORDINATE in self._template_content:
            self._coordinate = self._template_content[PDFTemplateConstant.PDF_COORDINATE]
        if PDFTemplateConstant.PDF_HEADER_TEXT in self._template_content:
            self._header_text = self._template_content[PDFTemplateConstant.PDF_HEADER_TEXT]
        if PDFTemplateConstant.PDF_SHOW_BORDER in self._template_content:
            self._show_border = self._template_content[PDFTemplateConstant.PDF_SHOW_BORDER]

    def set_pdf_file(self, file_name):
        if not isinstance(file_name, str):
            raise ValueError("file name is not str.")

        self._pdf_file = file_name

    def set_item_data(self, page_num, item_name, **kwargs):
        """
        设置各Item的相关数据
        :param page_num: page编号
        :param item_name: item名称
        :param kwargs: 相关参数Key-Value对
        :return:
        """
        _page_flag = "page%s" % page_num
        if _page_flag not in self._pages:
            raise ValueError("page number '%s' do not exist." % page_num)
        if item_name not in self._pages['page%d' % page_num][PDFTemplateConstant.PDF_ITEMS]:
            raise ValueError("%s has not item:%s." % (_page_flag, item_name))

        item = self._pages['page%d' % page_num][PDFTemplateConstant.PDF_ITEMS][item_name]

        for k, v in kwargs.items():
            item[k] = v
        item[PDFTemplateConstant.PDF_INVALID] = False

    def _set_pdf_info(self):
        """
        设置PDF文件的相关属性
        :return:
        """
        if self._author is not None:
            self._cv.setAuthor(self._author)
        if self._title is not None:
            self._cv.setTitle(self._title)

    def _get_valid_pages(self):
        """
        从模板文件中筛选出有效的Page
        :return:
        """
        max_page_num = 0
        valid_count = []

        for page in self._pages:
            page_num = int(page.replace("page", ""))
            if page_num < 0:
                raise ValueError("page num must >= 0.")
            if int(page_num) > max_page_num:
                max_page_num = int(page_num)

            page = self._pages[page]
            if not page[PDFTemplateConstant.PDF_INVALID]:
                valid_count.append(page_num)
        if max_page_num != len(self._pages) - 1:
            raise ValueError("page num discontinuous.")

        valid_count = sorted(valid_count)

        _pages = {}
        index = 0
        for page_num in valid_count:
            _pages[index] = {}

            page = self._pages['page%d' % page_num]

            _pages[index] = deepcopy(page)
            _pages[index][PDFTemplateConstant.PDF_ITEMS] = []
            for item_name in page[PDFTemplateConstant.PDF_ITEMS]:
                item = page[PDFTemplateConstant.PDF_ITEMS][item_name]
                if item[PDFTemplateConstant.PDF_INVALID] is True:
                    continue

                _pages[index][PDFTemplateConstant.PDF_ITEMS].append(item)

            index += 1

        return _pages

    @staticmethod
    def _auto_calc_position(pages):
        """
        自动计算各Page中Item的位置（自动排版）
        :param pages:
        :return:
        """
        add_count = 0

        _pages = {}
        for page_num in pages:
            page = pages[page_num]
            if page[PDFTemplateConstant.PDF_AUTO_POSITION] is True:
                # 需要自动排版
                next_page = PDFTemplatePage.calc_position(page)
                _pages[page_num + add_count] = deepcopy(page)
                while next_page:
                    # 需要分页
                    add_count += 1
                    _next_page = PDFTemplatePage.calc_position(next_page)
                    _pages[page_num + add_count] = deepcopy(next_page)

                    if _next_page:
                        next_page = deepcopy(_next_page)
                    else:
                        next_page = None
            else:
                # 不需要自动排版
                _pages[page_num + add_count] = deepcopy(pages[page_num])
        pages = deepcopy(_pages)
        del _pages

        return pages

    def _create_page_object(self, pages):
        """
        创建各Page的实例化对象
        :param pages:
        :return:
        """
        self._valid_pages = []

        for page_num in pages:
            page = pages[page_num]

            page_ins = PDFTemplatePage(page, page_num, self._page_size, coordinate=self._coordinate,
                                       header_text=self._header_text)

            self._valid_pages.append(page_ins)

    def draw(self):
        """
        生成PDF文件
        :return:
        """
        self._cv = canvas.Canvas(self._pdf_file, pagesize=self._page_size, bottomup=1)

        self._set_pdf_info()

        pages = self._get_valid_pages()
        pages = self._auto_calc_position(pages)
        self._create_page_object(pages)

        first_page = True
        for page_ins in self._valid_pages:
            if first_page is False:
                # 新开一页
                self._cv.showPage()
            if first_page is True:
                first_page = False

            # 画当前页
            page_ins.draw(self._cv, self._show_border)

        self._cv.save()
        self._cv = None
