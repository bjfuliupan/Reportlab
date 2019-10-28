# -*- coding: utf-8 -*-

import math
from reportlab.lib import colors
from reportlab.graphics.charts.barcharts import BarChart
from reportlab.lib.attrmap import AttrMap
from reportlab.lib.attrmap import AttrMapValue
from reportlab.lib.validators import isBoolean, OneOf, isListOfStringsOrNone, isListOfStrings, isNumber, isString, \
    isNumberInRange, isColor
from reportlab.graphics.shapes import Rect
from pdflib.ReportLabLib import ChartsLegend, ALL_COLORS, XCategoryAxisWithDesc, YCategoryAxisWithDesc, \
    YValueAxisWithDesc, XValueAxisWithDesc, DefaultFontName
from reportlab.graphics.shapes import String, STATE_DEFAULTS
from reportlab.pdfbase.pdfmetrics import stringWidth


class ReportLabBarChart(BarChart):

    _flipXY = 0

    _attrMap = AttrMap(
        BASE=BarChart,
        drawLegend=AttrMapValue(isBoolean, desc='If true draw legend.', advancedUsage=1),
        legendPositionType=AttrMapValue(
            OneOf("null", "top-left", "top-mid", "top-right", "bottom-left", "bottom-mid", "bottom-right"),
            desc="The position of LinLegend."),
        legendAdjustX=AttrMapValue(isNumber, desc='xxx.'),
        legendAdjustY=AttrMapValue(isNumber, desc='xxx.'),
        legendCategoryNames=AttrMapValue(isListOfStringsOrNone, desc='List of legend category names.'),
        titleMain=AttrMapValue(isString, desc='main title text.'),
        titleMainFontName=AttrMapValue(isString, desc='main title font name.'),
        titleMainFontSize=AttrMapValue(isNumberInRange(0, 100), desc='main title font size.'),
        titleMainFontColor=AttrMapValue(isColor, desc='main title font color.'),
        legendFontSize=AttrMapValue(isNumberInRange(0, 100), desc='legend text font size.'),
        x_labels_height=AttrMapValue(isNumberInRange(0, 100), desc='the max height in x-labels.'),
        y_labels_height=AttrMapValue(isNumberInRange(0, 50), desc='the max height in y-labels.')
    )

    def __init__(self, x, y, width, height, cat_names, data, step_count=4, style="parallel", label_format=None,
                 legend_names=None, legend_position="top-right", legend_adjust_x=0, legend_adjust_y=0,
                 main_title="", main_title_font_name=None, main_title_font_size=None, main_title_font_color=None,
                 x_desc=None, y_desc=None, cat_label_angle=30, cat_label_all=False):
        BarChart.__init__(self)

        if self._flipXY:
            self.categoryAxis = YCategoryAxisWithDesc(desc=y_desc)
            self.valueAxis = XValueAxisWithDesc(desc=x_desc)
        else:
            self.categoryAxis = XCategoryAxisWithDesc(desc=x_desc)
            self.valueAxis = YValueAxisWithDesc(desc=y_desc)

        if style not in ["stacked", "parallel"]:
            style = "parallel"
        self.categoryAxis.style = style

        self.valueAxis.visibleGrid = 1
        self.valueAxis.gridStrokeColor = colors.Color(0.5, 0.5, 0.5, 0.5)
        self.valueAxis.gridStrokeWidth = 1

        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.data = data
        self.strokeColor = colors.black
        self.categoryAxis.labels.boxAnchor = 'ne'
        # self.categoryAxis.labels.dx = 0
        # self.categoryAxis.labels.dy = 0
        self.categoryAxis.labels.angle = cat_label_angle
        # self.categoryAxis.labels.boxFillColor = colors.Color(1, 0, 0, 1)

        if cat_label_all is False:
            cat_names_num = len(cat_names)
            show_cat_num = 4
            if cat_names_num > show_cat_num:
                gap_num = int(cat_names_num / show_cat_num)
                for i in range(cat_names_num):
                    if i % gap_num != 0:
                        cat_names[i] = ""
        self.categoryAxis.categoryNames = cat_names

        if label_format is not None:
            self.barLabelFormat = label_format
            if len(data) > 1 and style == "stacked":
                self.barLabels.boxTarget = "mid"
            else:
                self.barLabels.boxTarget = "hi"
                self.barLabels.nudge = 15

        min_value, max_value, step = self.get_limit_value(step_count)

        self.valueAxis.valueMin = min_value
        self.valueAxis.valueMax = max_value
        self.valueAxis.valueStep = step

        self.drawLegend = False
        self.legendCategoryNames = None
        if legend_names is not None and isListOfStrings(legend_names) is True:
            self.drawLegend = True
            self.legendCategoryNames = legend_names
        self.legendPositionType = legend_position
        self.legendAdjustX = legend_adjust_x
        self.legendAdjustY = legend_adjust_y
        self.legendFontSize = 7

        self.titleMain = main_title
        self.titleMainFontName = DefaultFontName
        self.titleMainFontSize = STATE_DEFAULTS['fontSize']
        self.titleMainFontColor = colors.black
        if main_title_font_name is not None:
            self.titleMainFontName = main_title_font_name
        if main_title_font_size is not None:
            self.titleMainFontSize = main_title_font_size
        if main_title_font_color is not None:
            self.titleMainFontColor = main_title_font_color

        self.x_labels_height = 0
        self.y_labels_height = 0

    def get_limit_value(self, step_count):
        min_value = 0xffffffff
        max_value = 0 - min_value

        _data = []
        if self.categoryAxis.style == "stacked":
            flag = True
            for d in self.data:
                idx = 0
                for i in d:
                    if flag:
                        _data.append(i)
                    else:
                        _data[idx] += i
                    idx += 1
                flag = False

            for d in _data:
                if d > max_value:
                    max_value = d
            for d in self.data:
                for i in d:
                    if i < min_value:
                        min_value = i
        else:
            _data = self.data[:]

            for d in _data:
                for i in d:
                    if i > max_value:
                        max_value = i
                    if i < min_value:
                        min_value = i

        max_value += int(max_value / 10)
        max_value = int(max_value / 5) * 5
        min_value -= int(min_value / 10)
        min_value = int(min_value / 5) * 5

        step = int((max_value - min_value) / step_count)
        step = int(step / 5 + 1) * 5

        max_value = min_value + (step * step_count)

        return min_value, max_value, step

    def set_bar_color(self):
        if self.legendCategoryNames is None:
            self.legendCategoryNames = []
        legend_num = len(self.legendCategoryNames)
        data_num = len(self.data)
        for i in range(data_num):
            bar = self.bars[i]
            bar.strokeColor = ALL_COLORS[i]
            bar.fillColor = ALL_COLORS[i]
            if i >= legend_num:
                self.legendCategoryNames.append("unknown")

        legend_num = len(self.legendCategoryNames)
        temp_category_names = self.legendCategoryNames[:]
        if legend_num >= 1:
            self.legendCategoryNames = []
            color_name_pairs = [(0, name) for name in temp_category_names]

            legend_width = ChartsLegend.calc_legend_width(
                color_name_pairs, 10, 10, DefaultFontName, self.legendFontSize)
            per_legend_width = int(legend_width / legend_num)
            legend_num_per_row = int(self.width / per_legend_width)
            index = 0
            row_names = []
            for name in temp_category_names:
                row_names.append(name)
                index += 1
                if index == legend_num_per_row:
                    index = 0
                    self.legendCategoryNames.append(row_names)
                    row_names = []
            if len(row_names) > 0:
                self.legendCategoryNames.append(row_names)
        else:
            self.legendCategoryNames = temp_category_names

    def _draw_legend(self, g):
        legend_count = 0
        for i in range(len(self.legendCategoryNames)):
            legend = ChartsLegend()

            legend.positionType = self.legendPositionType
            if self.legendPositionType != "null":
                if self.legendPositionType in ["bottom-left", "bottom-mid", "bottom-right"]:
                    legend.backgroundRect = \
                        Rect(self.x,
                             self.y + legend.bottom_gap - self.x_labels_height - 15 - ((i + 1) * legend.fontSize),
                             self.width, self.height)
                else:
                    legend.backgroundRect = Rect(self.x, self.y + (i * legend.fontSize * 1.2), self.width, self.height)

            legend.adjustX = self.legendAdjustX
            legend.adjustY = self.legendAdjustY

            legend.fontSize = self.legendFontSize

            legend.colorNamePairs = []
            for j in range(len(self.legendCategoryNames[i])):
                legend.colorNamePairs.append((ALL_COLORS[legend_count + j],
                                              self.legendCategoryNames[i][j]))
            legend_count += len(self.legendCategoryNames[i])

            g.add(legend)

    def draw(self):
        self.set_bar_color()
        if self.drawLegend is True:
            if self.legendPositionType in ["bottom-left", "bottom-mid", "bottom-right"]:
                row_count = len(self.legendCategoryNames) + 1
                self.height -= row_count * self.legendFontSize
                self.y += row_count * self.legendFontSize

        g = BarChart.draw(self)

        if self.drawLegend is True:
            self._draw_legend(g)

        if self.titleMain != "":
            title = String(0, 0, self.titleMain)
            title.fontSize = self.titleMainFontSize
            title.fontName = self.titleMainFontName
            title.fillColor = self.titleMainFontColor
            title.textAnchor = 'start'
            # title.x = self.x - 20
            # title.y = self.y + self.height + 20
            title.x = 0
            title.y = self.y + self.height + 20

            g.add(title)

        return g


class ReportLabVerticalBarChart(ReportLabBarChart):

    _flipXY = 0

    def __init__(self, *args, **kwargs):
        ReportLabBarChart.__init__(self, *args, **kwargs)

    def _calc_labels_size(self):
        max_width = 0
        index = 0
        for label_text in self.categoryAxis.categoryNames:
            tmp_width = stringWidth(label_text, self.categoryAxis.labels.fontName, self.categoryAxis.labels.fontSize)
            if tmp_width > max_width:
                max_width = tmp_width

            if self.categoryAxis.labels[index].angle % 90 == 0:
                self.categoryAxis.labels[index].dx = \
                    int(tmp_width * math.cos(self.categoryAxis.labels[index].angle / 180 * math.pi) / 2) - \
                    int(self.categoryAxis.labels.fontSize *
                        math.sin(self.categoryAxis.labels[index].angle / 180 * math.pi)
                        / 2)
            index += 1

        self.x_labels_height = \
            int(max_width * math.sin(self.categoryAxis.labels.angle / 180 * math.pi)) + \
            int(self.categoryAxis.labels.fontSize * math.cos(self.categoryAxis.labels.angle / 180 * math.pi))
        self.y_labels_height = 0

        return self.x_labels_height, self.y_labels_height

    def _adjust_positon(self):
        self.x = 30
        if self.x_labels_height > 20:
            self.y = self.x_labels_height + 10
        else:
            self.y = 30
        self.width -= self.x + 30
        self.height -= self.y + self.titleMainFontSize + 20

    def draw(self):
        self._calc_labels_size()
        self._adjust_positon()

        return ReportLabBarChart.draw(self)


class ReportLabHorizontalBarChart(ReportLabBarChart):

    _flipXY = 1

    def __init__(self, *args, **kwargs):
        ReportLabBarChart.__init__(self, *args, **kwargs)

        # self.categoryAxis.labels.labelPosFrac = 0

    def _calc_labels_size(self):
        max_width = 0
        index = 0
        for label_text in self.categoryAxis.categoryNames:
            tmp_width = stringWidth(label_text, self.categoryAxis.labels.fontName, self.categoryAxis.labels.fontSize)
            if tmp_width > max_width:
                max_width = tmp_width

            if self.categoryAxis.labels[index].angle % 90 == 0:
                self.categoryAxis.labels[index].dy = \
                    int(tmp_width * math.sin(self.categoryAxis.labels[index].angle / 180 * math.pi) / 2) +  \
                    int(self.categoryAxis.labels.fontSize *
                        math.cos(self.categoryAxis.labels[index].angle / 180 * math.pi)
                        / 2)
            else:
                self.categoryAxis.labels[index].dy = \
                    int(self.categoryAxis.labels.fontSize *
                        math.cos(self.categoryAxis.labels[index].angle / 180 * math.pi))
            self.categoryAxis.labels[index].dx += \
                -self.categoryAxis.labels.fontSize * math.sin(self.categoryAxis.labels[index].angle / 180 * math.pi)
            index += 1

        self.x_labels_height = 5
        y_tmp = int(max_width * math.cos(self.categoryAxis.labels.angle / 180 * math.pi))
        self.y_labels_height = 50 if y_tmp > 50 else y_tmp

        return self.x_labels_height, self.y_labels_height

    def _adjust_positon(self):
        if self.y_labels_height > 20:
            self.x += self.y_labels_height + 10
        else:
            self.x += 30
        self.y += self.x_labels_height + 10
        self.width -= self.x + 30
        self.height -= self.x_labels_height + 10 + self.titleMainFontSize + 10 + 10

    def draw(self):
        self._calc_labels_size()
        self._adjust_positon()

        return ReportLabBarChart.draw(self)


if __name__ == "__main__":
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics import renderPDF

    drawing = Drawing(500, 1000)

    bc_cats1 = ["liupan", "lijie", "longhui", "zijian", "gaofeng", "yilin", "heng", "xuesong"]
    bc_values1 = [(170, 165, 167, 172, 176, 180, 160, 166), (60, 65, 55, 58, 70, 72, 68, 80)]
    bc_cats2 = ["liupan", "lijie", "longhui", "zijian", "gaofeng", "yilin", "heng", "xuesong"]
    bc_values2 = [(170, 165, 167, 172, 176, 180, 160, 166), (60, 65, 55, 58, 70, 72, 68, 80)]

    my_bar_charts1 = ReportLabVerticalBarChart(50, 800, 150, 125, bc_cats1, bc_values1, label_format="%s",
                                               legend_names=["刘攀", "lijie"], legend_position="bottom-right",
                                               x_desc="姓名", y_desc="身高/体重")
    my_bar_charts2 = ReportLabHorizontalBarChart(275, 800, 150, 125, bc_cats2, bc_values2, style="stacked",
                                                 legend_names=["liupan", "lijie"], legend_position="top-right",
                                                 main_title="My First PDF Test.刘攀", main_title_font_color=colors.blue,
                                                 x_desc="身高/体重", y_desc="姓名")

    drawing.add(my_bar_charts1)
    drawing.add(my_bar_charts2)

    renderPDF.drawToFile(drawing, 'example_barcharts.pdf')
