# -*- coding: utf-8 -*-

import json
import os
import collections
import xmltodict
from reportlab.graphics.shapes import Drawing, String, STATE_DEFAULTS, Line, Rect
# from reportlab.graphics import renderPDF
from reportlab.lib.validators import isListOfNumbers, isString, isNumber, isListOfStrings
from reportlab.lib.styles import getSampleStyleSheet  # , ParagraphStyle
from reportlab.platypus import Paragraph  # , SimpleDocTemplate  # , KeepTogether
from reportlab.pdfgen import canvas
# from reportlab.lib import colors
from reportlab.lib.colors import Color
from reportlab.pdfbase.pdfmetrics import stringWidth

from ReportLabLineCharts import ReportLabHorizontalLineChart
from ReportLabBarCharts import ReportLabHorizontalBarChart, ReportLabVerticalBarChart
from ReportLabPieCharts import ReportLabPieChart
from ReportLabLib import DefaultFontName


class PDFTemplate(object):

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

        if "items" not in template_content:
            raise ValueError("no items.")
        if PDFTemplate.is_dict(template_content['items']) is False:
            raise ValueError("items is not dict.")
        for it in template_content['items']:
            it = template_content['items'][it]
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
    def _draw_line_chart(format_json):
        width = format_json['rect'][2]
        height = format_json['rect'][3]

        d = Drawing(width, height, vAlign="TOP")

        x = 20  # format_json['rect'][0]
        y = 20  # format_json['rect'][1]
        width -= 40
        height -= 40
        if format_json['data'] is None or type(format_json['data']) is str:
            r = Rect(x, y, width, height, fillColor=Color(0.95, 0.95, 0.95, 1))
            d.add(r)

            width += 40
            height += 40
            text_format = {"rect": [int(width / 2), int(height / 2), width, height - 30],
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
        height -= 40
        if format_json['data'] is None or type(format_json['data']) is str:
            r = Rect(x, y, width, height, fillColor=Color(0.95, 0.95, 0.95, 1))
            d.add(r)

            width += 40
            height += 40
            text_format = {"rect": [int(width / 2), int(height / 2), width, height - 30],
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
                bar_chart = ReportLabHorizontalBarChart(x, y, width, height, cat_names, data, style=style,
                                                        label_format=label_format,  step_count=step_count,
                                                        legend_names=legend_names, legend_position=legend_position,
                                                        legend_adjust_x=legend_adjust_x, legend_adjust_y=legend_adjust_y,
                                                        main_title=main_title, main_title_font_name=main_title_font_name,
                                                        main_title_font_size=main_title_font_size,
                                                        main_title_font_color=main_title_font_color, x_desc=x_desc,
                                                        y_desc=y_desc)
            elif bar_style == "vertical":
                bar_chart = ReportLabVerticalBarChart(x, y, width, height, cat_names, data, style=style,
                                                      label_format=label_format,  step_count=step_count,
                                                      legend_names=legend_names, legend_position=legend_position,
                                                      legend_adjust_x=legend_adjust_x, legend_adjust_y=legend_adjust_y,
                                                      main_title=main_title, main_title_font_name=main_title_font_name,
                                                      main_title_font_size=main_title_font_size,
                                                      main_title_font_color=main_title_font_color, x_desc=x_desc,
                                                      y_desc=y_desc)
            if bar_chart is not None:
                d.add(bar_chart)

        return d

    @staticmethod
    def _draw_pie_chart(format_json):
        width = format_json['rect'][2]
        height = format_json['rect'][3]

        d = Drawing(width, height, vAlign="TOP")

        x = 20  # format_json['rect'][0]
        y = 20  # format_json['rect'][1]
        width -= 40
        height -= 40
        if format_json['data'] is None or type(format_json['data']) is str:
            r = Rect(x, y, width, height, fillColor=Color(0.95, 0.95, 0.95, 1))
            d.add(r)

            width += 40
            height += 40
            text_format = {"rect": [int(width / 2), int(height / 2), width, height - 30],
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

        if auto_calc:
            if position == "middle":
                x = int(width / 2)
                y = int(height / 2)
            elif position == "start":
                y = height
        else:
            x = format_json['rect'][0]
            y = format_json['rect'][1]

        text = String(x, y, content)

        text.fontName = DefaultFontName
        if "font_name" in format_json:
            text.fontName = format_json['font_name']
        if "font_size" in format_json:
            text.fontSize = format_json['font_size']
        if "font_color" in format_json:
            text.fillColor = format_json['font_color']
        text.textAnchor = position

        d.add(text)

        return d

    @staticmethod
    def _draw_paragraph(format_json):
        content = format_json['content']
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
        if indent_flag:
            stylesheet['BodyText'].firstLineIndent = word_width * 2
        stylesheet['BodyText'].leading = word_width * 1.5

        paragraph = Paragraph(content, stylesheet['BodyText'])
        if "force_top" in format_json and int(format_json['force_top']) == 1:
            _, h = paragraph.wrap(format_json['rect'][2], format_json['rect'][3])
            format_json['rect'][1] = format_json['rect'][1] + format_json['rect'][3] - h

        return paragraph

    @staticmethod
    def get_pages(items):
        max_page_num = 0
        valid_flag = {}
        for it in items:
            it = items[it]
            page_num = it['page_num']
            if page_num < 0:
                raise ValueError("page num must >= 0.")

            if page_num not in valid_flag:
                valid_flag[page_num] = False

            if it['invalid'] is False:
                valid_flag[page_num] = True

            if int(page_num) > max_page_num:
                max_page_num = int(page_num)
        if max_page_num != len(valid_flag) - 1:
            raise ValueError("page num discontinuous.")

        _pages = {}
        for i in range(max_page_num + 1):
            _pages[i] = []
        for it in items:
            it = items[it]
            if valid_flag[it['page_num']]:
                _pages[it['page_num']].append(it)

        delete_count = 0
        pages = {}
        for page_num in _pages:
            items = _pages[page_num]
            if len(items) == 0:
                delete_count += 1
                continue

            pages[page_num - delete_count] = items

        return pages

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
    def compute_coord(template_content):
        if "coordinate" not in template_content or template_content['coordinate'] != "left-top":
            return template_content

        page_height = template_content["page_size"][1]

        for item in template_content["items"]:
            item = template_content["items"][item]

            if "rect" in item:
                item['rect'][1] = page_height - item['rect'][1] - item['rect'][3]

        return template_content

    @staticmethod
    def _set_pdf_info(cv, template_content):
        if "author" in template_content:
            cv.setAuthor(template_content['author'])
        if "title" in template_content:
            cv.setTitle(template_content['title'])

    @staticmethod
    def draw(template_content):
        template_content = PDFTemplate.type_format(template_content)

        PDFTemplate.args_check(template_content)

        PDFTemplate.compute_coord(template_content)

        header_text = None
        if "header_text" in template_content:
            header_text = template_content["header_text"]
        page_size = template_content["page_size"]

        cv = canvas.Canvas(template_content['file_name'], pagesize=page_size, bottomup=1)

        PDFTemplate._set_pdf_info(cv, template_content)

        pages = PDFTemplate.get_pages(template_content['items'])
        pre_page = None
        for page_num in pages:
            if pre_page != page_num:
                if pre_page is not None:
                    cv.showPage()
                pre_page = page_num

                PDFTemplate._draw_header(cv, page_size, header_text)
                PDFTemplate._draw_feet(cv, page_size, page_num + 1)

            items = pages[page_num]
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

                if item is not None:
                    item.wrapOn(cv, it['rect'][2], it['rect'][3])
                    item.drawOn(cv, it['rect'][0], it['rect'][1])

        cv.save()

    @staticmethod
    def set_line_chart_data(json_data, data, category_names=None,
                            legend_names=None, main_title=None, x_desc=None, y_desc=None):
        json_data['data'] = data
        json_data['invalid'] = False

        if category_names is not None:
            json_data['category_names'] = category_names
        if legend_names is not None:
            json_data['legend_names'] = legend_names
        if main_title is not None:
            json_data['main_title'] = main_title
        if x_desc is not None:
            json_data['x_desc'] = x_desc
        if y_desc is not None:
            json_data['y_desc'] = y_desc

        return json_data

    @staticmethod
    def set_bar_chart_data(json_data, data, category_names=None, bar_style=None,
                           legend_names=None, main_title=None, x_desc=None, y_desc=None):
        json_data['data'] = data
        json_data['invalid'] = False

        if category_names is not None:
            json_data['category_names'] = category_names
        if bar_style is not None:
            json_data['bar_style'] = bar_style
        if legend_names is not None:
            json_data['legend_names'] = legend_names
        if main_title is not None:
            json_data['main_title'] = main_title
        if x_desc is not None:
            json_data['x_desc'] = x_desc
        if y_desc is not None:
            json_data['y_desc'] = y_desc

        return json_data

    @staticmethod
    def set_pie_chart_data(json_data, data, category_names=None, main_title=None):
        json_data['data'] = data
        json_data['invalid'] = False

        if category_names is not None:
            json_data['category_names'] = category_names
        if main_title is not None:
            json_data['main_title'] = main_title

        return json_data

    @staticmethod
    def set_text_data(json_data, content):
        json_data['content'] = content
        json_data['invalid'] = False

        return json_data

    @staticmethod
    def set_paragraph_data(json_data, content):
        json_data['content'] = content
        json_data['invalid'] = False

        return json_data

    @staticmethod
    def type_format(json_data):
        if "page_size" in json_data:
            json_data['page_size'] = json.loads(json_data['page_size'])

        if "items" in json_data:
            for it in json_data['items']:
                it = json_data['items'][it]
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

        return json_data

    @staticmethod
    def read_template(file_name):
        try:
            with open(file_name, "r", encoding='UTF-8') as f:
                template = f.read()

            template = xmltodict.parse(template)['pdf']

            for item in template['items']:
                item = template['items'][item]
                if "invalid" not in item:
                    item['invalid'] = True
                elif item['invalid'] == "True":
                    item['invalid'] = True
                elif item['invalid'] == "False":
                    item['invalid'] = False
                else:
                    item['invalid'] = True
        except Exception as err_info:
            print(err_info)
            return None

        return template


if __name__ == "__main__":
    pass
