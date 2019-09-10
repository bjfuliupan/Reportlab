# -*- coding: utf-8 -*-

import math
from reportlab.lib import colors
from reportlab.lib.attrmap import AttrMap
from reportlab.lib.attrmap import AttrMapValue
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.lib.validators import isBoolean, OneOf, isListOfStringsOrNone, isListOfStrings, isNumber, isString, \
    isNumberInRange, isColor
from reportlab.graphics.shapes import Rect
from reportlab.graphics.shapes import String, STATE_DEFAULTS
from pdflib.ReportLabLib import ChartsLegend, ALL_COLORS, XCategoryAxisWithDesc, YValueAxisWithDesc, DefaultFontName, \
    get_string_width
# from reportlab.pdfbase.pdfmetrics import stringWidth


class LegendedHorizontalLineChart(HorizontalLineChart):
    """A subclass of Legend for drawing legends with lines as the
    swatches rather than rectangles. Useful for lineCharts and
    linePlots. Should be similar in all other ways the the standard
    Legend class.
    """

    _attrMap = AttrMap(
        BASE=HorizontalLineChart,
        drawLegend=AttrMapValue(isBoolean, desc='If true draw legend.', advancedUsage=1),
        legendPositionType=AttrMapValue(
            OneOf(
                "null",
                "top-left", "top-mid", "top-right",
                "bottom-left", "bottom-mid", "bottom-right"
            ),
            desc="The position of LinLegend."),
        legendAdjustX=AttrMapValue(isNumber, desc='xxx.'),
        legendAdjustY=AttrMapValue(isNumber, desc='xxx.'),
        legendCategoryNames=AttrMapValue(isListOfStringsOrNone, desc='List of legend category names.'),
        titleMain=AttrMapValue(isString, desc='main title text.'),
        titleMainFontName=AttrMapValue(isString, desc='main title font name.'),
        titleMainFontSize=AttrMapValue(isNumberInRange(0, 100), desc='main title font size.'),
        titleMainFontColor=AttrMapValue(isColor, desc='main title font color.'),
        legendFontSize=AttrMapValue(isNumberInRange(0, 100), desc='legend text font size.'),
        labels_height=AttrMapValue(isNumberInRange(0, 100), desc='the max height of x-labels.')
    )

    def __init__(self):
        HorizontalLineChart.__init__(self)

        self.drawLegend = False
        self.legendPositionType = "null"
        self.legendCategoryNames = None
        self.legendAdjustX = 0
        self.legendAdjustY = 0
        self.titleMain = ""
        self.titleMainFontColor = colors.gray
        self.titleMainFontName = DefaultFontName
        self.titleMainFontSize = STATE_DEFAULTS['fontSize']

        self.legendFontSize = 7

        self.labels_height = 0

    def set_line_color(self):
        if self.legendCategoryNames is None:
            self.legendCategoryNames = []
        legend_num = len(self.legendCategoryNames)
        data_num = len(self.data)
        for i in range(data_num):
            line = self.lines[i]
            line.strokeColor = ALL_COLORS[i]
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

    def _calc_labels_size(self):
        max_width = 0
        index = 0
        for label_text in self.categoryAxis.categoryNames:
            tmp_width = get_string_width(label_text, self.categoryAxis.labels.fontName,
                                         self.categoryAxis.labels.fontSize)
            if tmp_width > max_width:
                max_width = tmp_width

            if self.categoryAxis.labels[index].angle % 90 == 0:
                self.categoryAxis.labels[index].dx = \
                    int(tmp_width * math.cos(self.categoryAxis.labels[index].angle / 180 * math.pi) / 2) - \
                    int(self.categoryAxis.labels.fontSize *
                        math.sin(self.categoryAxis.labels[index].angle / 180 * math.pi)
                        / 2)
            index += 1

        self.labels_height = \
            int(max_width * math.sin(self.categoryAxis.labels.angle / 180 * math.pi)) + \
            int(self.categoryAxis.labels.fontSize * math.cos(self.categoryAxis.labels.angle / 180 * math.pi))

        return self.labels_height

    def _adjust_positon(self):
        self.x = 30
        if self.labels_height > 20:
            self.y = self.labels_height + 10
        else:
            self.y = 30
        self.width -= self.x + 30
        self.height -= self.y + self.titleMainFontSize + 20

    def draw(self):
        self._calc_labels_size()
        self._adjust_positon()

        self.set_line_color()
        if self.drawLegend is True:
            if self.legendPositionType in ["bottom-left", "bottom-mid", "bottom-right"]:
                row_count = len(self.legendCategoryNames) + 1
                self.height -= row_count * self.legendFontSize
                self.y += row_count * self.legendFontSize

        g = HorizontalLineChart.draw(self)

        if self.drawLegend:
            for i in range(len(self.legendCategoryNames)):
                legend = ChartsLegend()

                legend.positionType = self.legendPositionType
                if self.legendPositionType != "null":
                    if self.legendPositionType in ["bottom-left", "bottom-mid", "bottom-right"]:
                        legend.backgroundRect = \
                            Rect(self.x,
                                 self.y + legend.bottom_gap - self.labels_height - 15 - ((i+1) * legend.fontSize),
                                 self.width, self.height)
                    else:
                        legend.backgroundRect = Rect(self.x, self.y - (i * legend.fontSize * 1.2),
                                                     self.width, self.height)

                legend.adjustX = self.legendAdjustX
                legend.adjustY = self.legendAdjustY

                legend.fontSize = self.legendFontSize

                legend.colorNamePairs = []
                for j in range(len(self.legendCategoryNames[i])):
                    legend.colorNamePairs.append((ALL_COLORS[i * len(self.legendCategoryNames[i]) + j],
                                                  self.legendCategoryNames[i][j]))

                g.add(legend)

        if self.titleMain != "":
            title = String(0, 0, self.titleMain)
            title.fontSize = self.titleMainFontSize
            title.fontName = self.titleMainFontName
            title.fillColor = self.titleMainFontColor
            title.textAnchor = 'start'
            title.x = self.x - 20
            title.y = self.y + self.height + 20

            g.add(title)

        return g


class ReportLabHorizontalLineChart(LegendedHorizontalLineChart):

    def __init__(self,
                 x, y, width, height, cat_names, data,
                 step_count=4, legend_names=None, legend_position="top-right", legend_adjust_x=0, legend_adjust_y=0,
                 main_title="", main_title_font_name=None, main_title_font_size=None, main_title_font_color=None,
                 x_desc=None, y_desc=None, cat_label_angle=30, cat_label_all=False):
        LegendedHorizontalLineChart.__init__(self)

        self.categoryAxis = XCategoryAxisWithDesc(desc=x_desc)
        self.valueAxis = YValueAxisWithDesc(desc=y_desc)

        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.data = data

        if cat_label_all is False:
            cat_names_num = len(cat_names)
            show_cat_num = 7
            if cat_names_num > show_cat_num:
                gap_num = int(cat_names_num / show_cat_num)
                for i in range(cat_names_num):
                    if i % gap_num != 0:
                        cat_names[i] = ""

        self.categoryAxis.categoryNames = cat_names
        self.categoryAxis.labels.boxAnchor = 'n'

        min_value, max_value, step = self.get_limit_value(step_count)
        self.valueAxis.valueMin = min_value
        self.valueAxis.valueMax = max_value
        self.valueAxis.valueStep = step

        self.joinedLines = 1
        self.lines.strokeWidth = 2

        if legend_names is not None and isListOfStrings(legend_names) is True:
            self.drawLegend = True
            self.legendCategoryNames = legend_names
        self.legendPositionType = legend_position

        self.legendAdjustX = legend_adjust_x
        self.legendAdjustY = legend_adjust_y

        self.titleMain = main_title
        if main_title_font_name is not None:
            self.titleMainFontName = main_title_font_name
        if main_title_font_size is not None:
            self.titleMainFontSize = main_title_font_size
        self.titleMainFontColor = colors.black
        if main_title_font_color is not None:
            self.titleMainFontColor = main_title_font_color

        self.categoryAxis.labels.boxAnchor = 'ne'
        self.categoryAxis.labels.dx = 0
        self.categoryAxis.labels.angle = cat_label_angle
        # self.categoryAxis.labels.boxFillColor = colors.Color(1, 0, 0, 1)

    def get_limit_value(self, step_count):
        min_value = 0xffffffff
        max_value = 0 - min_value

        for d in self.data:
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

        max_value = min_value + (step_count * step)

        return min_value, max_value, step


if __name__ == "__main__":
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics import renderPDF

    drawing = Drawing(500, 1000)

    lc_cats1 = ["一月", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"]
    lc_values1 = [(13, 5, 20, 22, 37, 45, 19, 4), (5, 20, 46, 38, 23, 21, 6, 14), (67, 88, 98, 13, 68, 109, 110, 120),
                  (6, 9, 77, 88, 91, 130, 135, 125)]
    lc_cats2 = ["刘攀", "lijie", "longhui", "zijian", "gaofeng", "yilin", "heng", "xuesong"]
    lc_values2 = [(170, 165, 167, 172, 176, 180, 160, 166), (60, 65, 55, 58, 70, 72, 68, 80)]

    my_line_charts1 = ReportLabHorizontalLineChart(50, 800, 400, 125, lc_cats1, lc_values1,
                                                   legend_names=["刘攀", "lijie", "longhui", "gaofeng"],
                                                   legend_position="bottom-mid",
                                                   main_title="My first PDF Test.刘攀",
                                                   main_title_font_color=colors.blue,
                                                   x_desc="月份", y_desc="数量")
    my_line_charts2 = ReportLabHorizontalLineChart(50, 600, 400, 125, lc_cats2, lc_values2,
                                                   legend_names=["刘攀", "lijie"],
                                                   legend_position="bottom-mid",
                                                   main_title="My second PDF Test.",
                                                   x_desc="Name", y_desc="身高/体重")

    drawing.add(my_line_charts1)
    drawing.add(my_line_charts2)

    renderPDF.drawToFile(drawing, 'example_linecharts.pdf')
