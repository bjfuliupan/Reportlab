# -*- coding: utf-8 -*-

from reportlab.lib import colors
from reportlab.graphics.charts.piecharts import Pie
from reportlab.lib.attrmap import AttrMap
from reportlab.lib.attrmap import AttrMapValue
from reportlab.lib.validators import isString, isNumberInRange, isColor
from reportlab.graphics.shapes import String, STATE_DEFAULTS
from pdflib.ReportLabLib import DefaultFontName


class ReportLabPieChart(Pie):
    _attrMap = AttrMap(
        BASE=Pie,
        titleMain=AttrMapValue(isString, desc='main title text.'),
        titleMainFontName=AttrMapValue(isString, desc='the font name of main title.'),
        titleMainFontSize=AttrMapValue(isNumberInRange(0, 100), desc='the font size of main title.'),
        titleMainFontColor=AttrMapValue(isColor, desc='the font color of main title.')
    )

    def __init__(self, x, y, width, height, cat_names, data,
                 main_title="", main_title_font_name=None, main_title_font_size=None, main_title_font_color=None):
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

    def draw(self):
        g = Pie.draw(self)

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
