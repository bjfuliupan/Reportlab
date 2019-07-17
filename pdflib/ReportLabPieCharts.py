# -*- coding: utf-8 -*-

from reportlab.lib import colors
from reportlab.graphics.charts.piecharts import Pie
from reportlab.lib.attrmap import AttrMap
from reportlab.lib.attrmap import AttrMapValue
from reportlab.lib.validators import isString, isNumberInRange, isColor, isBoolean, OneOf, isNumber, \
    isListOfStringsOrNone, isListOfStrings
from reportlab.graphics.shapes import String, STATE_DEFAULTS, Rect
from pdflib.ReportLabLib import DefaultFontName, ALL_COLORS, ChartsLegend
from reportlab.pdfbase.pdfmetrics import stringWidth


class ReportLabPieChart(Pie):
    _attrMap = AttrMap(
        BASE=Pie,
        titleMain=AttrMapValue(isString, desc='main title text.'),
        titleMainFontName=AttrMapValue(isString, desc='the font name of main title.'),
        titleMainFontSize=AttrMapValue(isNumberInRange(0, 100), desc='the font size of main title.'),
        titleMainFontColor=AttrMapValue(isColor, desc='the font color of main title.'),
        drawLegend=AttrMapValue(isBoolean, desc='If true draw legend.', advancedUsage=1),
        legendCategoryNames=AttrMapValue(isListOfStringsOrNone, desc='List of legend category names.'),
        legendPositionType=AttrMapValue(
            OneOf("null", "right"),
            desc="The position of LinLegend."),
        legendAdjustX=AttrMapValue(isNumber, desc='xxx.'),
        legendAdjustY=AttrMapValue(isNumber, desc='xxx.'),
        legendFontSize=AttrMapValue(isNumberInRange(0, 100), desc='legend text font size.'),
        legendFontName=AttrMapValue(isString, desc='the font name of legend text.')
    )

    def __init__(self, x, y, width, height, cat_names, data,
                 main_title="", main_title_font_name=None, main_title_font_size=None, main_title_font_color=None,
                 legend_position="right", legend_adjust_x=0, legend_adjust_y=0, draw_legend=False):
        Pie.__init__(self)

        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.data = data
        self.labels = cat_names

        self.sideLabels = 1
        # max_i, max_value = self.get_limit_value()
        # self.slices[max_i].popout = 10
        # self.slices[max_i].strokeWidth = 2
        # # self.slices[max_i].strokeDashArray = [2, 2]
        # self.slices[max_i].fontColor = colors.red
        self.slices.fontName = DefaultFontName
        self.slices.strokeWidth = 0.5

        self.titleMain = main_title
        self.titleMainFontName = DefaultFontName
        self.titleMainFontSize = STATE_DEFAULTS['fontSize']
        self.titleMainFontColor = colors.gray
        if main_title_font_name is not None:
            self.titleMainFontName = main_title_font_name
        if main_title_font_size is not None:
            self.titleMainFontSize = main_title_font_size
        if main_title_font_color is not None:
            self.titleMainFontColor = main_title_font_color

        self.drawLegend = draw_legend
        self.legendCategoryNames = []
        if self.drawLegend is True:
            self.labels = None

            if isListOfStrings(cat_names) is True:
                self.legendCategoryNames = cat_names
            self.legendPositionType = legend_position
            self.legendAdjustX = legend_adjust_x
            self.legendAdjustY = legend_adjust_y
            self.legendFontSize = 7
            self.legendFontName = DefaultFontName

            self.slices.strokeColor = colors.Color(0, 0, 0, 0)
            self.slices.fontColor = colors.Color(0, 0, 0, 0)
            self.sideLabels = 0

    def get_limit_value(self):
        max_value = -9999999
        i = 0
        max_i = 0
        for d in self.data:
            if d > max_value:
                max_value = d
                max_i = i
            i += 1

        return max_i, max_value

    def set_bar_color(self):
        if self.legendCategoryNames is None:
            self.legendCategoryNames = []
        legend_num = len(self.legendCategoryNames)
        data_num = len(self.data)
        for i in range(data_num):
            _slice = self.slices[i]
            if self.drawLegend is False:
                _slice.strokeColor = ALL_COLORS[i]
            _slice.fillColor = ALL_COLORS[i]
            if i >= legend_num:
                self.legendCategoryNames.append(("unknown", str(self.data[i])))
            else:
                self.legendCategoryNames[i] = (self.legendCategoryNames[i], " "+str(self.data[i]))

    def _calc_position(self):
        self.x += 30
        self.y += 30
        if self.width > self.height:
            self.width = self.height
        else:
            self.height = self.width
        self.width -= 60
        self.height -= 60

    def _draw_legend(self, g):
        max_width = []
        cn_len = len(self.legendCategoryNames)
        for i in range(len(self.legendCategoryNames[0])):
            max_width.append(0)

        for i in range(cn_len):
            for str_i in range(len(self.legendCategoryNames[i])):
                tmp_width = stringWidth(self.legendCategoryNames[i][str_i],
                                        self.legendFontName, self.legendFontSize) + 2
                if tmp_width > max_width[str_i]:
                    max_width[str_i] = tmp_width

        for i in range(cn_len):
            legend = ChartsLegend()

            legend.positionType = self.legendPositionType
            if self.legendPositionType != "null":
                legend.backgroundRect = \
                    Rect(self.x + 5, self.y - (i * int(self.legendFontSize * 1.5)), self.width, self.height)

            legend.adjustX = self.legendAdjustX
            legend.adjustY = self.legendAdjustY

            legend.fontSize = self.legendFontSize

            if type(self.legendCategoryNames[i]) is tuple:
                for str_i in range(len(self.legendCategoryNames[i])):
                    sub_col = legend.subCols[str_i]
                    sub_col.align = 'left'
                    sub_col.minWidth = max_width[str_i]
            legend.colorNamePairs = []
            legend.colorNamePairs.append((ALL_COLORS[i], self.legendCategoryNames[i]))

            g.add(legend)

    def draw(self):
        self.set_bar_color()

        self._calc_position()

        g = Pie.draw(self)

        if self.drawLegend is True:
            self._draw_legend(g)

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


if __name__ == "__main__":
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics import renderPDF

    drawing = Drawing(500, 1000)

    pc_cats1 = ["刘攀", "lijie", "longhui", "zijian", "gaofeng", "yilin", "heng", "xuesong"]
    pc_values1 = [170, 165, 167, 172, 176, 180, 160, 166]

    my_pie_charts1 = ReportLabPieChart(50, 800, 150, 150, pc_cats1, pc_values1,
                                       main_title="My First Pie PDF Test.刘攀")

    drawing.add(my_pie_charts1)

    renderPDF.drawToFile(drawing, 'example_piecharts.pdf')
