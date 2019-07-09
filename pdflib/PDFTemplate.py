# -*- coding: utf-8 -*-

import json
import collections
import xmltodict
from copy import deepcopy
from reportlab.graphics.shapes import Drawing, String, STATE_DEFAULTS, Line, Rect
# from reportlab.graphics import renderPDF
from reportlab.lib.validators import isListOfNumbers, isString, isNumber, isListOfStrings
from reportlab.lib.styles import getSampleStyleSheet  # , ParagraphStyle
from reportlab.platypus import Paragraph  # , SimpleDocTemplate  # , KeepTogether
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.colors import Color
from reportlab.pdfbase.pdfmetrics import stringWidth

from pdflib.ReportLabLineCharts import ReportLabHorizontalLineChart
from pdflib.ReportLabBarCharts import ReportLabHorizontalBarChart, ReportLabVerticalBarChart
from pdflib.ReportLabPieCharts import ReportLabPieChart
from pdflib.ReportLabLib import DefaultFontName
from reportlab.platypus import Table, TableStyle


class PDFTemplate(object):

    paragraph_leading = 1.5

    def __init__(self):
        pass

    @staticmethod
    def args_check_line_chart(it):
        if "rect" not in it:
            raise ValueError("line chart no rect.")
        # if "category_names" not in it:
        #     raise ValueError("line chart no category_names.")
        if "data" not in it:
            raise ValueError("line chart no data.")

        if isListOfNumbers(it['rect']) is False:
            raise ValueError("line chart rect error.")

    @staticmethod
    def args_check_bar_chart(it):
        if "rect" not in it:
            raise ValueError("bar chart no rect.")
        # if "category_names" not in it:
        #     raise ValueError("bar chart no category_names.")
        if "bar_style" not in it:
            raise ValueError("bar chart no bar_style.")
        if "data" not in it:
            raise ValueError("bar chart no data.")

        if isListOfNumbers(it['rect']) is False:
            raise ValueError("bar chart rect error.")

    @staticmethod
    def args_check_pie_chart(it):
        if "rect" not in it:
            raise ValueError("pie chart no rect.")
        # if "category_names" not in it:
        #     raise ValueError("pie chart no category_names.")
        if "data" not in it:
            raise ValueError("pie chart no data.")

        if isListOfNumbers(it['rect']) is False:
            raise ValueError("pie chart rect error.")

    @staticmethod
    def is_dict(data):
        data_type = type(data)
        if data_type is dict or data_type is collections.OrderedDict:
            return True

        return False

    @staticmethod
    def type_format(json_data):
        if "page_size" in json_data:
            json_data['page_size'] = json.loads(json_data['page_size'])

        if "show_border" in json_data:
            if json_data['show_border'] == "True":
                json_data['show_border'] = True
            elif json_data['show_border'] == "False":
                json_data['show_border'] = False
            else:
                json_data['show_border'] = False
        else:
            json_data['show_border'] = False

        if "pages" in json_data:
            for page in json_data['pages']:
                page = json_data['pages'][page]
                if "rect" in page:
                    page['rect'] = json.loads(page['rect'])

                if "auto_position" in page:
                    if page['auto_position'] == "True":
                        page['auto_position'] = True
                    elif page['auto_position'] == "False":
                        page['auto_position'] = False
                    else:
                        page['auto_position'] = False
                else:
                    page['auto_position'] = False

                if "x-padding" in page:
                    page['x-padding'] = int(page['x-padding'])
                else:
                    page['x-padding'] = 0

                if "y-padding" in page:
                    page['y-padding'] = int(page['y-padding'])
                else:
                    page['y-padding'] = 0

                if "align-type" not in page:
                    page['align-type'] = "middle"

                if "items" in page:
                    for it in page['items']:
                        it = page['items'][it]
                        it_type = it['type']

                        if "page_num" in it:
                            it["page_num"] = int(it["page_num"])
                        if "rect" in it:
                            it['rect'] = json.loads(it['rect'])
                        if "category_names" in it and type(it['category_names']) is str:
                            it['category_names'] = json.loads(it['category_names'])
                        if "font_color" in it:
                            it["font_color"] = eval(it["font_color"])
                        if "main_title_font_color" in it:
                            it["main_title_font_color"] = eval(it["main_title_font_color"])
                        if "font_size" in it:
                            it["font_size"] = int(it["font_size"])
                        if "main_title_font_size" in it:
                            it["main_title_font_size"] = int(it["main_title_font_size"])
                        if "indent_flag" in it:
                            it["indent_flag"] = int(it["indent_flag"])

                        if it_type == "paragraph":
                            if "style" not in it:
                                it['style'] = "BodyText"

        return json_data

    @staticmethod
    def args_check(template_content):
        if PDFTemplate.is_dict(template_content) is False:
            raise ValueError("template content is not dict.")

        if "file_name" not in template_content:
            raise ValueError("no file name.")
        if isString(template_content['file_name']) is False:
            raise ValueError("file name error.")

        if "page_size" not in template_content:
            raise ValueError("no page size.")
        if isListOfNumbers(template_content['page_size']) is False:
            raise ValueError("page size error.")
        if len(template_content['page_size']) != 2:
            raise ValueError("page size error.")

        if "coordinate" not in template_content:
            raise ValueError("no page coordinate-system.")
        if template_content['coordinate'] != "left-top":
            raise ValueError("coordinate must be left-top. other not support auto_position.")

        if "pages" not in template_content:
            raise ValueError("no pages.")
        if PDFTemplate.is_dict(template_content['pages']) is False:
            raise ValueError("pages is not dict.")
        for page in template_content['pages']:
            page = template_content['pages'][page]
            if "rect" not in page:
                raise ValueError("page no rect.")
            for it in page['items']:
                it = page['items'][it]
                if PDFTemplate.is_dict(it) is False:
                    raise ValueError("item is not dict.")
                if "type" not in it:
                    raise ValueError("item no type.")

                if it['type'] == 'line_chart':
                    PDFTemplate.args_check_line_chart(it)
                elif it['type'] == 'bar_chart':
                    PDFTemplate.args_check_bar_chart(it)
                elif it['type'] == 'pie_chart':
                    PDFTemplate.args_check_pie_chart(it)

    @staticmethod
    def _draw_chart_rect(d, x, y, width, height, format_json):
        r = Rect(x, y, width, height, fillColor=Color(0.95, 0.95, 0.95, 1))
        d.add(r)

        width += 40
        height += 40
        text_format = {"rect": [int(width / 2), int(height / 2), width, height],
                       "content": "暂无数据", "position": "middle",
                       "font_name": DefaultFontName, "font_size": 30, "font_color": Color(0.5, 0.5, 0.5, 1)}
        t = PDFTemplate._draw_text(text_format)
        d.add(t)

        if "main_title" in format_json:
            text_format = {"rect": [0, height, width, height - 15],
                           "content": format_json['main_title'], "position": "start",
                           "font_name": DefaultFontName, "font_size": 15, "font_color": Color(0.5, 0.5, 0.5, 1)}
            if "main_title_font_name" in format_json:
                text_format['font_name'] = format_json['main_title_font_name']
            if "main_title_font_size" in format_json:
                text_format['font_size'] = format_json['main_title_font_size']
            if "main_title_font_color" in format_json:
                text_format['font_color'] = format_json['main_title_font_color']
            main_title = PDFTemplate._draw_text(text_format)
            d.add(main_title)

    @staticmethod
    def _draw_line_chart(format_json):
        width = format_json['rect'][2]
        height = format_json['rect'][3]

        d = Drawing(width, height, vAlign="TOP")

        x = 20  # format_json['rect'][0]
        y = 20  # format_json['rect'][1]
        width -= 40
        height -= 50
        if format_json['data'] is None or type(format_json['data']) is str:
            PDFTemplate._draw_chart_rect(d, x, y, width, height, format_json)
        elif type(format_json['data']) is list:
            cat_names = format_json['category_names']
            data = format_json['data']

            step_count = 4
            if "step_count" in format_json and isNumber(format_json['step_count']) is True:
                step_count = format_json['step_count']
            legend_names = None
            if "legend_names" in format_json and isListOfStrings(format_json['legend_names']) is True:
                legend_names = format_json['legend_names']
            legend_position = "top-right"
            if "legend_position" in format_json and isString(format_json['legend_position']) is True:
                legend_position = format_json['legend_position']
            legend_adjust_x = 0
            if "legend_adjust_x" in format_json and isNumber(format_json['legend_adjust_x']) is True:
                legend_adjust_x = format_json['legend_adjust_x']
            legend_adjust_y = 0
            if "legend_adjust_y" in format_json and isNumber(format_json['legend_adjust_y']) is True:
                legend_adjust_y = format_json['legend_adjust_y']
            main_title = ""
            if "main_title" in format_json and isString(format_json['main_title']) is True:
                main_title = format_json['main_title']
            main_title_font_name = None
            if "main_title_font_name" in format_json and isString(format_json['main_title_font_name']) is True:
                main_title_font_name = format_json['main_title_font_name']
            main_title_font_size = None
            if "main_title_font_size" in format_json and isNumber(format_json['main_title_font_size']) is True:
                main_title_font_size = format_json['main_title_font_size']
            main_title_font_color = None
            if "main_title_font_color" in format_json:
                main_title_font_color = format_json['main_title_font_color']
            x_desc = None
            if "x_desc" in format_json and isString(format_json['x_desc']) is True:
                x_desc = format_json['x_desc']
            y_desc = None
            if "y_desc" in format_json and isString(format_json['y_desc']) is True:
                y_desc = format_json['y_desc']

            line_chart = ReportLabHorizontalLineChart(x, y, width, height, cat_names, data, step_count=step_count,
                                                      legend_names=legend_names, legend_position=legend_position,
                                                      legend_adjust_x=legend_adjust_x, legend_adjust_y=legend_adjust_y,
                                                      main_title=main_title, main_title_font_name=main_title_font_name,
                                                      main_title_font_size=main_title_font_size,
                                                      main_title_font_color=main_title_font_color,
                                                      x_desc=x_desc, y_desc=y_desc)
            d.add(line_chart)

        return d

    @staticmethod
    def _draw_bar_chart(format_json):
        width = format_json['rect'][2]
        height = format_json['rect'][3]

        d = Drawing(width, height, vAlign="TOP")

        x = 20  # format_json['rect'][0]
        y = 20  # format_json['rect'][1]
        width -= 40
        height -= 50
        if format_json['data'] is None or type(format_json['data']) is str:
            PDFTemplate._draw_chart_rect(d, x, y, width, height, format_json)
        elif type(format_json['data']) is list:
            cat_names = format_json['category_names']
            data = format_json['data']
            bar_style = format_json['bar_style']

            style = "parallel"
            if "style" in format_json and isString(format_json['style']) is True:
                style = format_json['style']
            label_format = None
            if "label_format" in format_json and isString(format_json['label_format']) is True:
                label_format = format_json['label_format']
            step_count = 4
            if "step_count" in format_json and isNumber(format_json['step_count']) is True:
                step_count = format_json['step_count']
            legend_names = None
            if "legend_names" in format_json and isListOfStrings(format_json['legend_names']) is True:
                legend_names = format_json['legend_names']
            legend_position = "top-right"
            if "legend_position" in format_json and isString(format_json['legend_position']) is True:
                legend_position = format_json['legend_position']
            legend_adjust_x = 0
            if "legend_adjust_x" in format_json and isNumber(format_json['legend_adjust_x']) is True:
                legend_adjust_x = format_json['legend_adjust_x']
            legend_adjust_y = 0
            if "legend_adjust_y" in format_json and isNumber(format_json['legend_adjust_y']) is True:
                legend_adjust_y = format_json['legend_adjust_y']
            main_title = ""
            if "main_title" in format_json and isString(format_json['main_title']) is True:
                main_title = format_json['main_title']
            main_title_font_name = None
            if "main_title_font_name" in format_json and isString(format_json['main_title_font_name']) is True:
                main_title_font_name = format_json['main_title_font_name']
            main_title_font_size = None
            if "main_title_font_size" in format_json and isNumber(format_json['main_title_font_size']) is True:
                main_title_font_size = format_json['main_title_font_size']
            main_title_font_color = None
            if "main_title_font_color" in format_json:
                main_title_font_color = format_json['main_title_font_color']
            x_desc = None
            if "x_desc" in format_json and isString(format_json['x_desc']) is True:
                x_desc = format_json['x_desc']
            y_desc = None
            if "y_desc" in format_json and isString(format_json['y_desc']) is True:
                y_desc = format_json['y_desc']

            bar_chart = None
            if bar_style == "horizontal":
                bar_chart = ReportLabHorizontalBarChart(
                    x, y, width, height, cat_names, data, style=style,
                    label_format=label_format,  step_count=step_count,
                    legend_names=legend_names, legend_position=legend_position,
                    legend_adjust_x=legend_adjust_x, legend_adjust_y=legend_adjust_y,
                    main_title=main_title, main_title_font_name=main_title_font_name,
                    main_title_font_size=main_title_font_size,
                    main_title_font_color=main_title_font_color, x_desc=x_desc, y_desc=y_desc)
            elif bar_style == "vertical":
                bar_chart = ReportLabVerticalBarChart(
                    x, y, width, height, cat_names, data, style=style,
                    label_format=label_format,  step_count=step_count,
                    legend_names=legend_names, legend_position=legend_position,
                    legend_adjust_x=legend_adjust_x, legend_adjust_y=legend_adjust_y,
                    main_title=main_title, main_title_font_name=main_title_font_name,
                    main_title_font_size=main_title_font_size,
                    main_title_font_color=main_title_font_color, x_desc=x_desc, y_desc=y_desc)
            if bar_chart is not None:
                d.add(bar_chart)

        return d

    @staticmethod
    def _draw_pie_chart(format_json):
        width = format_json['rect'][2]
        height = format_json['rect'][3]

        d = Drawing(width, height, vAlign="TOP")

        x = 30  # format_json['rect'][0]
        y = 30  # format_json['rect'][1]
        width -= 60
        height -= 60
        if format_json['data'] is None or type(format_json['data']) is str:
            PDFTemplate._draw_chart_rect(d, x, y, width, height, format_json)
        elif type(format_json['data']) is list:
            cat_names = format_json['category_names']
            data = format_json['data']

            main_title = ""
            if "main_title" in format_json and isString(format_json['main_title']) is True:
                main_title = format_json['main_title']
            main_title_font_name = None
            if "main_title_font_name" in format_json and isString(format_json['main_title_font_name']) is True:
                main_title_font_name = format_json['main_title_font_name']
            main_title_font_size = None
            if "main_title_font_size" in format_json and isNumber(format_json['main_title_font_size']) is True:
                main_title_font_size = format_json['main_title_font_size']
            main_title_font_color = None
            if "main_title_font_color" in format_json:
                main_title_font_color = format_json['main_title_font_color']

            pie_chart = ReportLabPieChart(x, y, width, height, cat_names, data, main_title=main_title,
                                          main_title_font_name=main_title_font_name,
                                          main_title_font_size=main_title_font_size,
                                          main_title_font_color=main_title_font_color)
            d.add(pie_chart)

        return d

    @staticmethod
    def _draw_text(format_json, auto_calc=True):
        width = format_json['rect'][2]
        height = format_json['rect'][3]

        d = Drawing(width, height, vAlign="TOP")

        content = format_json['content']
        position = format_json['position']
        x = 0  # format_json['x']
        y = 0  # format_json['y']

        font_size = STATE_DEFAULTS['fontSize']
        if "font_size" in format_json:
            font_size = format_json['font_size']

        if auto_calc:
            if position == "middle":
                x = int(width / 2)
                y = int(height / 2) - int(font_size / 2)
            elif position == "start":
                y = height
        else:
            x = format_json['rect'][0]
            y = format_json['rect'][1]

        text = String(x, y, content)

        text.fontName = DefaultFontName
        if "font_name" in format_json:
            text.fontName = format_json['font_name']
        text.fontSize = font_size
        if "font_color" in format_json:
            text.fillColor = format_json['font_color']
        text.textAnchor = position

        d.add(text)

        return d

    @staticmethod
    def _draw_table(format_json):
        """
        :param format_json:
        :return:
        """

        font_name = DefaultFontName
        if "font_name" in format_json:
            font_name = format_json['font_name']
        font_size = STATE_DEFAULTS['fontSize']
        if "font_size" in format_json:
            font_size = format_json['font_size']
        font_color = STATE_DEFAULTS['fontSize']
        if "font_color" in format_json:
            font_color = format_json['font_color']
        indent_flag = 0
        if "indent_flag" in format_json:
            indent_flag = format_json['indent_flag']

        word_width = stringWidth(" ", font_name, font_size) * 2

        # style = ParagraphStyle(
        #     name='Normal',
        #     fontName=font_name,
        #     fontSize=font_size,
        #     fillColor=font_color
        # )
        stylesheet = getSampleStyleSheet()
        stylesheet['BodyText'].fontName = font_name
        stylesheet['BodyText'].fontSize = font_size
        stylesheet['BodyText'].fillColor = font_color

        if "columns" not in format_json:
            raise ValueError("don't have any columns infomation. ")

        cols = format_json["columns"]

        # columns names
        data = cols.items().values()

        # generate table style
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.burlywood),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.red),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ])
        content = format_json["content"]

        # merage data
        data.extend(content)
        table = Table(data)
        table.setStyle(style)

        return table

    @staticmethod
    def _draw_paragraph(format_json):
        content = format_json['content']
        style_name = format_json['style']
        font_name = DefaultFontName
        if "font_name" in format_json:
            font_name = format_json['font_name']

        stylesheet = getSampleStyleSheet()
        ss = stylesheet[style_name]
        ss.fontName = font_name

        if "font_size" in format_json:
            ss.fontSize = format_json['font_size']

        if "font_color" in format_json:
            ss.fillColor = format_json['font_color']

        word_width = stringWidth(" ", font_name, ss.fontSize) * 2
        ss.leading = word_width * PDFTemplate.paragraph_leading

        indent_flag = 0
        if "indent_flag" in format_json:
            indent_flag = format_json['indent_flag']
        if indent_flag:
            ss.firstLineIndent = word_width * 2

        paragraph = Paragraph(content, ss)
        if "force_top" in format_json and int(format_json['force_top']) == 1:
            _, h = paragraph.wrap(format_json['rect'][2], format_json['rect'][3])
            format_json['rect'][1] = format_json['rect'][1] + format_json['rect'][3] - h

        return paragraph

    @staticmethod
    def get_pages(pages):
        max_page_num = 0
        valid_count = []

        for page in pages:
            page_num = int(page.replace("page", ""))
            if page_num < 0:
                raise ValueError("page num must >= 0.")
            if int(page_num) > max_page_num:
                max_page_num = int(page_num)

            page = pages[page]
            if not page['invalid']:
                valid_count.append(page_num)
        if max_page_num != len(pages) - 1:
            raise ValueError("page num discontinuous.")

        valid_count = sorted(valid_count)

        _pages = {}
        index = 0
        for page_num in valid_count:
            _pages[index] = {
                'items': [],
                'rect': [],
                'auto_position': False,
                'x-padding': 0,
                'y-padding': 0,
                'align-type': ""
            }

            page = pages['page%d' % page_num]

            _pages[index]['rect'] = page['rect']
            _pages[index]['auto_position'] = page['auto_position']
            _pages[index]['x-padding'] = page['x-padding']
            _pages[index]['y-padding'] = page['y-padding']
            _pages[index]['align-type'] = page['align-type']
            for item in page['items']:
                item = page['items'][item]
                if item['invalid'] is True:
                    continue

                _pages[index]['items'].append(item)

            index += 1

        return _pages

    @staticmethod
    def _draw_header(cv, page_size, content=None):
        start_x = int(page_size[0] / 10)

        width = page_size[0]
        height = int(page_size[1] / 20)

        d = Drawing(width, height, vAlign="TOP")

        header_line = Line(start_x, 0, width - start_x, 0)
        d.add(header_line)

        if content is not None:
            x = int(width / 2)
            y = 5

            text = String(x, y, content)
            text.fontName = DefaultFontName
            text.textAnchor = "middle"

            d.add(text)

        d.wrapOn(cv, width, height)
        d.drawOn(cv, 0, page_size[1] - height)

    @staticmethod
    def _draw_feet(cv, page_size, page_num=None):
        start_x = int(page_size[0] / 10)

        width = page_size[0]
        height = int(page_size[1] / 20)

        d = Drawing(width, height, vAlign="TOP")

        feet_line = Line(start_x, height, width - start_x, height)
        d.add(feet_line)

        if page_num is not None:
            x = int(width / 2)
            y = height - STATE_DEFAULTS['fontSize']

            text = String(x, y, str(page_num))
            text.fontName = DefaultFontName
            text.textAnchor = "middle"

            d.add(text)

        d.wrapOn(cv, width, height)
        d.drawOn(cv, 0, 0)

    @staticmethod
    def compute_coord(pages, page_height, left_top):
        for page_num in pages:
            page = pages[page_num]
            for item in page['items']:
                if "rect" in item:
                    item['rect'][0] = item['rect'][0] + page['rect'][0]
                    item['rect'][1] = item['rect'][1] + page['rect'][1]
                    if left_top:
                        item['rect'][1] = page_height - item['rect'][1] - item['rect'][3]

        return pages

    @staticmethod
    def _set_pdf_info(cv, template_content):
        if "author" in template_content:
            cv.setAuthor(template_content['author'])
        if "title" in template_content:
            cv.setTitle(template_content['title'])

    @staticmethod
    def _draw_border(cv, x, y, width, height, color):
        d = Drawing(width, height)
        r = Rect(0, 0, width, height, strokeColor=color, fillColor=Color(0, 0, 0, 0))
        d.add(r)
        d.drawOn(cv, x, y)

    @staticmethod
    def _draw_page(cv, items, show_border=False):
        for it in items:
            item = None
            if it['type'] == 'line_chart':
                item = PDFTemplate._draw_line_chart(it)
            elif it['type'] == 'bar_chart':
                item = PDFTemplate._draw_bar_chart(it)
            elif it['type'] == 'pie_chart':
                item = PDFTemplate._draw_pie_chart(it)
            elif it['type'] == 'text':
                item = PDFTemplate._draw_text(it)
            elif it['type'] == 'paragraph':
                item = PDFTemplate._draw_paragraph(it)
            elif it['type'] == 'table':
                item = PDFTemplate._draw_table(it)

            if show_border:
                PDFTemplate._draw_border(cv, it['rect'][0], it['rect'][1], it['rect'][2], it['rect'][3],
                                         Color(1, 0, 0, 1))

            if item is not None:
                item.wrapOn(cv, it['rect'][2], it['rect'][3])
                item.drawOn(cv, it['rect'][0], it['rect'][1])

    @staticmethod
    def _prepare_draw(template_content):
        template_content = PDFTemplate.type_format(template_content)

        PDFTemplate.args_check(template_content)

    @staticmethod
    def _calc_positon_align(page, page_width, x_padding, start_index, end_index, align_type):
        if align_type == "middle" or align_type == "right":
            items_width = (end_index - start_index - 1) * x_padding
            for i in range(end_index - start_index):
                items_width += page['items'][start_index + i]['rect'][2]

            start_pos = 0
            if align_type == "middle":
                start_pos = int((page_width - items_width) / 2)
            elif align_type == "right":
                start_pos = page_width - items_width

            for i in range(end_index - start_index):
                page['items'][start_index + i]['rect'][0] = start_pos
                start_pos += page['items'][start_index + i]['rect'][2] + x_padding
        elif align_type == "left":
            pass

    @staticmethod
    def _calc_paragraph_height(item):
        p = PDFTemplate._draw_paragraph(item)
        _, h = p.wrap(item['rect'][2], 0)
        del p
        return h

    @staticmethod
    def _auto_set_paragraph_height(item):
        item['rect'][3] = PDFTemplate._calc_paragraph_height(item)

    @staticmethod
    def _split_paragraph_text_by_height(item, split_height):
        content = item['content']
        str_len = len(content)
        content_height = PDFTemplate._calc_paragraph_height(item)
        split_index = int(split_height / content_height * str_len)

        tmp_item = deepcopy(item)
        tmp_item['content'] = content[:split_index]
        content_height = PDFTemplate._calc_paragraph_height(tmp_item)
        del tmp_item

        if content_height > split_height:
            flag = 0
        else:
            flag = 1

        while split_index > 0 or split_index < str_len:
            if flag == 0:
                split_index -= 1
            else:
                split_index += 1

            tmp_item = deepcopy(item)
            tmp_item['content'] = content[:split_index]
            tmp_height = PDFTemplate._calc_paragraph_height(tmp_item)
            del tmp_item

            if flag == 0:
                if tmp_height <= split_height:
                    split_index -= 1
                    break
            else:
                if tmp_height >= split_height:
                    split_index -= 1
                    break

        return split_index

    @staticmethod
    def _split_paragraph(items, index, page_height):
        item = items[index]
        if item['type'] != "paragraph":
            return False

        item_height = item['rect'][3]
        y = item['rect'][1]
        if item_height + y <= page_height:
            return True

        split_height = page_height - y
        split_index = PDFTemplate._split_paragraph_text_by_height(item, split_height)

        new_item = deepcopy(item)
        new_item['content'] = new_item['content'][split_index:]
        new_item['indent_flag'] = 0

        item['content'] = item['content'][:split_index]
        item['rect'][3] = split_height

        items.insert(index + 1, new_item)

        return True

    @staticmethod
    def _calc_positon(page):
        next_page = deepcopy(page)
        next_page['items'] = []

        page_width = page['rect'][2]
        page_height = page['rect'][3]
        x_padding = page['x-padding']
        y_padding = page['y-padding']
        align_type = page['align-type']

        cur_x = 0
        cur_y = 0
        next_y = 0
        next_page_flag = False
        index = 0
        next_page_index = 0
        row_start = 0

        for item in page['items']:
            if item['type'] == "paragraph":
                PDFTemplate._auto_set_paragraph_height(item)

            item_width = item['rect'][2]
            item_height = item['rect'][3]

            if cur_x != 0 and cur_x + item_width > page_width:
                PDFTemplate._calc_positon_align(page, page_width, x_padding, row_start, index, align_type)

                next_page_index = index
                row_start = index
                item['rect'][0] = 0
                item['rect'][1] = next_y
                cur_x = item_width + x_padding
                cur_y = next_y
                next_y = cur_y + item_height + y_padding
            else:
                item['rect'][0] = cur_x
                item['rect'][1] = cur_y
                cur_x += item_width + x_padding
                if cur_y + item_height + y_padding > next_y:
                    next_y = cur_y + item_height + y_padding

            if next_y > page_height:
                if cur_y != 0 or item['type'] == "paragraph":
                    if item['type'] == "paragraph":
                        split_flag = PDFTemplate._split_paragraph(page['items'], index, page_height)
                        if split_flag:
                            next_page_index += 1
                            index += 1
                    next_page_flag = True
                    break

            index += 1
        PDFTemplate._calc_positon_align(page, page_width, x_padding, row_start, index, align_type)

        if next_page_flag:
            next_page['items'] = page['items'][next_page_index:]
            page['items'] = page['items'][:next_page_index]
            return next_page

        return None

    @staticmethod
    def _auto_calc_position(pages):
        add_count = 0

        _pages = {}
        for page_num in pages:
            page = pages[page_num]
            if page['auto_position'] is True:
                next_page = PDFTemplate._calc_positon(page)
                _pages[page_num + add_count] = deepcopy(page)
                while next_page:
                    add_count += 1
                    _next_page = PDFTemplate._calc_positon(next_page)
                    _pages[page_num + add_count] = deepcopy(next_page)

                    if _next_page:
                        next_page = deepcopy(_next_page)
                    else:
                        next_page = None
            else:
                _pages[page_num + add_count] = deepcopy(pages[page_num])
        pages = deepcopy(_pages)
        del _pages

        return pages

    @staticmethod
    def draw(template_content):
        PDFTemplate._prepare_draw(template_content)

        header_text = None
        if "header_text" in template_content:
            header_text = template_content["header_text"]
        page_size = template_content["page_size"]
        show_border = template_content["show_border"]

        cv = canvas.Canvas(template_content['file_name'], pagesize=page_size, bottomup=1)

        PDFTemplate._set_pdf_info(cv, template_content)

        pages = PDFTemplate.get_pages(template_content['pages'])
        pages = PDFTemplate._auto_calc_position(pages)
        if "coordinate" in template_content and template_content['coordinate'] == "left-top":
            PDFTemplate.compute_coord(pages, page_size[1], True)
        else:
            PDFTemplate.compute_coord(pages, page_size[1], False)

        pre_page = None
        for page_num in pages:
            if pre_page != page_num:
                if pre_page is not None:
                    cv.showPage()
                pre_page = page_num

                PDFTemplate._draw_header(cv, page_size, header_text)
                PDFTemplate._draw_feet(cv, page_size, page_num + 1)

            if show_border:
                PDFTemplate._draw_border(cv, pages[page_num]['rect'][0], pages[page_num]['rect'][1],
                                         pages[page_num]['rect'][2], pages[page_num]['rect'][3], Color(0, 0, 1, 1))
            PDFTemplate._draw_page(cv, pages[page_num]['items'], show_border)

        cv.save()

    @staticmethod
    def set_table_data(pages, page_num, item_name, data):
        item = pages['page%d' % page_num]['items'][item_name]
        item['data'] = data
        item['invalid'] = False
        return pages

    @staticmethod
    def set_line_chart_data(pages, page_num, item_name, data, category_names=None,
                            legend_names=None, main_title=None, x_desc=None, y_desc=None):
        item = pages['page%d' % page_num]['items'][item_name]
        item['data'] = data
        item['invalid'] = False

        if category_names is not None:
            item['category_names'] = category_names
        if legend_names is not None:
            item['legend_names'] = legend_names
        if main_title is not None:
            item['main_title'] = main_title
        if x_desc is not None:
            item['x_desc'] = x_desc
        if y_desc is not None:
            item['y_desc'] = y_desc

        return pages

    @staticmethod
    def set_bar_chart_data(pages, page_num, item_name, data, category_names=None, bar_style=None,
                           legend_names=None, main_title=None, x_desc=None, y_desc=None):
        item = pages['page%d' % page_num]['items'][item_name]
        item['data'] = data
        item['invalid'] = False

        if category_names is not None:
            item['category_names'] = category_names
        if bar_style is not None:
            item['bar_style'] = bar_style
        if legend_names is not None:
            item['legend_names'] = legend_names
        if main_title is not None:
            item['main_title'] = main_title
        if x_desc is not None:
            item['x_desc'] = x_desc
        if y_desc is not None:
            item['y_desc'] = y_desc

        return pages

    @staticmethod
    def set_pie_chart_data(pages, page_num, item_name, data, category_names=None, main_title=None):
        item = pages['page%d' % page_num]['items'][item_name]
        item['data'] = data
        item['invalid'] = False

        if category_names is not None:
            item['category_names'] = category_names
        if main_title is not None:
            item['main_title'] = main_title

        return pages

    @staticmethod
    def set_text_data(pages, page_num, item_name, content):
        item = pages['page%d' % page_num]['items'][item_name]
        item['content'] = content
        item['invalid'] = False

        return pages

    @staticmethod
    def set_paragraph_data(pages, page_num, item_name, content):
        item = pages['page%d' % page_num]['items'][item_name]
        item['content'] = content
        item['invalid'] = False

        return pages

    @staticmethod
    def read_template(file_name):
        try:
            with open(file_name, "r", encoding='UTF-8') as f:
                template = f.read()

            template = xmltodict.parse(template)['pdf']

            for page in template['pages']:
                page = template['pages'][page]
                if "invalid" not in page:
                    page['invalid'] = False
                elif page['invalid'] == "True":
                    page['invalid'] = True
                elif page['invalid'] == "False":
                    page['invalid'] = False
                else:
                    page['invalid'] = False

                for item in page['items']:
                    item = page['items'][item]
                    if "invalid" not in item:
                        item['invalid'] = False
                    elif item['invalid'] == "True":
                        item['invalid'] = True
                    elif item['invalid'] == "False":
                        item['invalid'] = False
                    else:
                        item['invalid'] = False
        except Exception as err_info:
            import traceback
            traceback.print_exc()
            print(err_info)
            return None

        return template
