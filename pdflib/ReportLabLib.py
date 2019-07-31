# -*- coding: utf-8 -*-

from reportlab.lib import colors
from reportlab.lib.attrmap import AttrMap
from reportlab.lib.attrmap import AttrMapValue
from reportlab.graphics.charts.legends import LineLegend
from reportlab.lib.validators import OneOf, isNumber
from reportlab.graphics.charts.axes import XCategoryAxis, YCategoryAxis, YValueAxis, XValueAxis
from reportlab.lib.validators import isString
from reportlab.graphics.shapes import String
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth

pdfmetrics.registerFont(TTFont('SimSun', 'SimSun.ttf'))
DefaultFontName = "SimSun"

ALL_COLORS = [
    colors.red,
    colors.green,
    colors.blue,
    colors.pink,
    colors.yellow,
    colors.black,
    colors.blueviolet,
    colors.brown,
    colors.burlywood,
    colors.cadetblue,
    colors.chartreuse,
    colors.chocolate,
    colors.coral,
    colors.cornsilk,
    colors.crimson,
    colors.cyan,
    colors.darkblue,
    colors.darkcyan,
    colors.darkgoldenrod,
    colors.darkgray,
    colors.darkgreen,
    colors.darkkhaki,
    colors.darkmagenta,
    colors.darkolivegreen,
    colors.darkorange,
    colors.darkorchid,
    colors.darkred,
    colors.darksalmon,
    colors.darkseagreen,
    colors.darkslateblue,
    colors.darkslategray,
    colors.darkslategrey,
    colors.darkturquoise,
    colors.darkviolet,
    colors.deeppink,
    colors.deepskyblue,
    colors.dimgray,
    colors.dodgerblue,
    colors.firebrick,
    colors.floralwhite,
    colors.forestgreen,
    colors.fuchsia,
    colors.gainsboro,
    colors.ghostwhite,
    colors.goldenrod,
    colors.greenyellow,
    colors.honeydew,
    colors.hotpink,
    colors.indianred,
    colors.indigo,
    colors.ivory,
    colors.khaki,
    colors.lavender,
    colors.lavenderblush,
    colors.lawngreen,
    colors.lemonchiffon,
    colors.lightblue,
    colors.lightcoral,
    colors.lightcyan,
    colors.lightgoldenrodyellow,
    colors.lightgreen,
    colors.lightgrey,
    colors.lightpink,
    colors.lightsalmon,
    colors.lightseagreen,
    colors.lightskyblue,
    colors.lightslategray,
    colors.lightslategrey,
    colors.lightsteelblue,
    colors.lightyellow,
    colors.lime,
    colors.limegreen,
    colors.linen,
    colors.magenta,
    colors.maroon,
    colors.mediumaquamarine,
    colors.mediumblue,
    colors.mediumorchid,
    colors.mediumpurple,
    colors.mediumseagreen,
    colors.mediumslateblue,
    colors.mediumspringgreen,
    colors.mediumturquoise
]


class ChartsLegend(LineLegend):
    """A subclass of Legend for drawing legends with lines as the
    swatches rather than rectangles. Useful for lineCharts and
    linePlots. Should be similar in all other ways the the standard
    Legend class.
    """

    _attrMap = AttrMap(
        BASE=LineLegend,
        positionType=AttrMapValue(
            OneOf(
                "null",
                "top-left", "top-mid", "top-right",
                "bottom-left", "bottom-mid", "bottom-right",
                "right"
            ),
            desc="The position of LinLegend."),
        backgroundRect=AttrMapValue(None, desc="The position of LinLegend."),
        adjustX=AttrMapValue(isNumber, desc='xxx.'),
        adjustY=AttrMapValue(isNumber, desc='xxx.'),
        bottom_gap=AttrMapValue(isNumber, desc='xxx.')
    )

    def __init__(self):
        LineLegend.__init__(self)

        self.positionType = "null"
        self.backgroundRect = None
        self.adjustX = 0
        self.adjustY = 0
        self.fontName = DefaultFontName
        self.deltax = 10
        self.deltay = 0
        self.boxAnchor = 'w'
        self.columnMaximum = 1
        self.yGap = 0
        self.fontSize = 7
        self.alignment = 'right'
        self.dxTextSpace = 5

        self.bottom_gap = 40

    @staticmethod
    def calc_legend_width(color_name_pairs, dx, deltax, font_name, font_size, sub_cols=None):
        pairs_num = len(color_name_pairs)

        max_text_width = 0
        x_width = 0
        for x in color_name_pairs:
            if type(x[1]) is tuple:
                for str_i in x[1]:
                    tmp_width = stringWidth(str(str_i), font_name, font_size)
                    if sub_cols is not None and tmp_width < sub_cols[0].minWidth:
                        tmp_width = sub_cols[0].minWidth
                    x_width += tmp_width
            else:
                str_x = x[1]
                x_width = stringWidth(str_x, font_name, font_size)
            if x_width > max_text_width:
                max_text_width = x_width
        total_text_width = (pairs_num - 1) * max_text_width + x_width

        legend_width = total_text_width + (dx * pairs_num) + (deltax * pairs_num)

        return legend_width

    def draw(self):
        legend_width = self.calc_legend_width(self.colorNamePairs, self.dx, self.deltax, self.fontName, self.fontSize,
                                              self.subCols)

        if self.positionType != "null" and self.backgroundRect is not None:
            if self.positionType == "top-left":
                self.x = self.backgroundRect.x
                self.y = self.backgroundRect.y + self.backgroundRect.height
            elif self.positionType == "top-mid":
                self.x = self.backgroundRect.x + int(self.backgroundRect.width / 2) - int(legend_width / 2)
                self.y = self.backgroundRect.y + self.backgroundRect.height
            elif self.positionType == "top-right":
                self.x = self.backgroundRect.x + self.backgroundRect.width - legend_width
                self.y = self.backgroundRect.y + self.backgroundRect.height
            elif self.positionType == "bottom-left":
                self.x = self.backgroundRect.x
                self.y = self.backgroundRect.y - self.bottom_gap
            elif self.positionType == "bottom-mid":
                self.x = self.backgroundRect.x + int(self.backgroundRect.width / 2) - int(legend_width / 2)
                self.y = self.backgroundRect.y - self.bottom_gap
            elif self.positionType == "bottom-right":
                self.x = self.backgroundRect.x + self.backgroundRect.width - legend_width
                self.y = self.backgroundRect.y - self.bottom_gap
            elif self.positionType == "right":
                self.x = self.backgroundRect.x + self.backgroundRect.width + 10
                self.y = self.backgroundRect.y + self.backgroundRect.height

            self.x += self.adjustX
            self.y += self.adjustY

        return LineLegend.draw(self)


def make_desc_test(self, flag):
    desc_text = None

    if flag not in ["X", "Y"]:
        return desc_text

    if self.desc is not None:
        desc_text = String(0, 0, self.desc)
        # title.fontSize = self.titleMainFontSize
        desc_text.fontName = DefaultFontName
        # title.fillColor = self.titleMainFontColor
        desc_text.textAnchor = 'start'

        if flag == "X":
            desc_text.x = self._x + self._length + 5
            desc_text.y = self._y - 5
        elif flag == "Y":
            desc_text.x = self._x - int(stringWidth(self.desc, desc_text.fontName, desc_text.fontSize) / 2)
            desc_text.y = self._y + self._length + 5

    return desc_text


class XCategoryAxisWithDesc(XCategoryAxis):

    _attrMap = AttrMap(
        BASE=XCategoryAxis,
        desc=AttrMapValue(None, desc="The description of the X axis.")
    )

    def __init__(self, desc=None):
        XCategoryAxis.__init__(self)

        self.desc = None
        if isString(desc) is True:
            self.desc = desc

        self.labels.fontName = DefaultFontName

    def makeTickLabels(self):
        g = XCategoryAxis.makeTickLabels(self)

        desc_text = make_desc_test(self, "X")
        if desc_text is not None:
            g.add(desc_text)

        return g


class YCategoryAxisWithDesc(YCategoryAxis):

    _attrMap = AttrMap(
        BASE=YCategoryAxis,
        desc=AttrMapValue(None, desc="The description of the Y axis.")
    )

    def __init__(self, desc=None):
        YCategoryAxis.__init__(self)

        self.desc = None
        if isString(desc) is True:
            self.desc = desc

        self.labels.fontName = DefaultFontName

    def makeTickLabels(self):
        g = YCategoryAxis.makeTickLabels(self)

        desc_text = make_desc_test(self, "Y")
        if desc_text is not None:
            g.add(desc_text)

        return g


class XValueAxisWithDesc(XValueAxis):

    _attrMap = AttrMap(
        BASE=XValueAxis,
        desc=AttrMapValue(None, desc="The description of the X axis.")
    )

    def __init__(self, desc=None):
        XValueAxis.__init__(self)

        self.desc = None
        if isString(desc) is True:
            self.desc = desc

    def makeTickLabels(self):
        g = XValueAxis.makeTickLabels(self)

        desc_text = make_desc_test(self, "X")
        if desc_text is not None:
            g.add(desc_text)

        return g


class YValueAxisWithDesc(YValueAxis):

    _attrMap = AttrMap(
        BASE=YValueAxis,
        desc=AttrMapValue(None, desc="The description of the Y axis.")
    )

    def __init__(self, desc=None):
        YValueAxis.__init__(self)

        self.desc = None
        if isString(desc) is True:
            self.desc = desc

    def makeTickLabels(self):
        g = YValueAxis.makeTickLabels(self)

        desc_text = make_desc_test(self, "Y")
        if desc_text is not None:
            g.add(desc_text)

        return g


def list_eval(list_str):
    if not isinstance(list_str, str):
        raise ValueError("not str.")

    if list_str == "None":
        return None

    if list_str[0] != '[' or list_str[-1] != ']':
        raise ValueError("not list format.")

    return eval(list_str)


def tuple_eval(list_str):
    if not isinstance(list_str, str):
        raise ValueError("not str.")

    if list_str == "None":
        return None

    if list_str[0] != '(' or list_str[-1] != ')':
        raise ValueError("not tuple format.")

    return eval(list_str)


def dict_eval(list_str):
    if not isinstance(list_str, str):
        raise ValueError("not str.")

    if list_str == "None":
        return None

    if list_str[0] != '{' or list_str[-1] != '}':
        raise ValueError("not dict format.")

    return eval(list_str)


def color_eval(list_str):
    if not isinstance(list_str, str):
        raise ValueError("not str.")

    if list_str.find("Color(") != 0 or list_str[-1] != ')':
        raise ValueError("not dict format.")

    _list_str = list_str.replace("Color", "colors.Color")
    return eval(_list_str)
