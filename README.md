# Reportlab
Reportlab

## 1 PDF模板结构
```
pdf													
    file_name                                  生成的PDF文件的路径。必填项
    author                                     PDF文件作者。默认为空
    title                                      PDF文件标题。默认为空
    page_size                                  每页的大小，格式：[width, height]。必填项
    coordinate                                 坐标系，取值：left-top、left-bottom。rect使用的坐标系。默认为left-top
    header_text                                页眉显示的文字。默认为空
    show_border                                是否显示各page和item的边界，用于debug或初期调试位置。取值：True、False。默认为False
    pages												
        page0											
            rect                               当前页的有效区域。格式：[x, y, width, height]。必填项
            auto_position                      是否自动排版。取值：True、False。默认为False
            x-padding                          水平方向各item之间的间距。设置自动排版时有效。默认为0
            y-padding                          垂直方向各item之间的间距。设置自动排版时有效。默认为0
            align-type                         水平方向上各item的对齐方式。取值：middle、left、right。设置自动排版时有效。默认为middle
            invalid                            是否无效。取值：True、False。默认为False。当设为True时，该页不显示。默认为False
            items										
                [item_name1]									
                    type                       text。该item为文本段。必填项
                    rect                       该item的绘画区域。格式：[x, y, width, height]。该坐标相对于page的rect而言。必填项
                    content                    该文本段的内容。必填项
                    position                   对齐方式。取值：middle、left、right。相对于该item的rect而言。默认为left
                    font_name                  字体名称。默认为SimSun
                    font_color                 字体颜色。格式：Color(r, g, b, a)，r、g、b和a的取值范围：[0, 1]。默认为黑色Color(0, 0, 0, 1)
                    font_size                  字体大小。默认为10
                    margin-left                该item的左间距。取值：整数。正数增加间距，负数缩小间距。默认为0
                    margin-right               该item的右间距。取值：整数。正数增加间距，负数缩小间距。默认为0
                    margin-up                  该item的上间距。取值：整数。正数增加间距，负数缩小间距。默认为0
                    margin-bottom              该item的下间距。取值：整数。正数增加间距，负数缩小间距。默认为0
                    invalid                    是否无效。取值：True、False。默认为False。当设为True时，该item不显示。默认为False
                /[item_name1]									
                                                    
                [item_name2]									
                    type                       paragraph。该item为段落。必填项
                    rect                       该item的绘画区域。格式：[x, y, width, height]。该坐标相对于page的rect而言。必填项
                    content                    该段落的内容。必填项
                    style                      段落的style，各style包括自己的字体、行间距等信息。取值：Normal、BodyText、Italic、Heading1、Heading2、
                                               Heading3、Heading4、Heading5、Heading6、Bullet、Definition。默认不设置style
                    font_name                  字体名称。未设置style时，默认为SimSun
                    font_color                 字体颜色。格式：Color(r, g, b, a)，r、g、b和a的取值范围：[0, 1]。未设置style时，默认为黑色Color(0, 0, 0, 1)
                    font_size                  字体大小。未设置style时，默认为10
                    indent_flag                段落开头是否缩进。取值：0、1。1是缩进两个word大小，0是不缩进。默认是0
                    margin-left                该item的左间距。取值：整数。正数增加间距，负数缩小间距。默认为0
                    margin-right               该item的右间距。取值：整数。正数增加间距，负数缩小间距。默认为0
                    margin-up                  该item的上间距。取值：整数。正数增加间距，负数缩小间距。默认为0
                    margin-bottom              该item的下间距。取值：整数。正数增加间距，负数缩小间距。默认为0
                    invalid                    是否无效。取值：True、False。默认为False。当设为True时，该item不显示。默认为False
                /[item_name2]									
                                                    
                [item_name3]									
                    type                       line_chart。该item为折线图。必填项
                    rect                       该item的绘画区域。格式：[x, y, width, height]。该坐标相对于page的rect而言。必填项
                    data                       折线图的数据。格式：[(数据集1), (数据集2), …]。必填项
                    main_title                 主标题的内容
                    main_title_font_name       主标题的字体名称。默认为SimSun
                    main_title_font_color      主标题的字体颜色。格式：Color(r, g, b, a)，r、g、b和a的取值范围：[0, 1]。默认为黑色Color(0, 0, 0, 1)
                    main_title_font_size       主标题的字体大小。默认为10
                    x_desc                     x轴的描述信息。默认为空
                    y_desc                     y轴的描述信息。默认为空
                    legend_names               legend的名称。和data一一对应，格式：[数据集1的名称, 数据集2的名称, …]。默认为空
                    legend_position            legend的位置。取值：top-left、top-middle、top-right、bottom-left、bottom-middle、bottom-right。默认为top-right
                    legend_adjust_x	           调整legend在X轴方向的位置。取值：整数。默认为0
                    legend_adjust_y	           调整legend在Y轴方向的位置。取值：整数。默认为0
                    step_count                 Y轴的数值格数。取值：正整数。默认为4
                    cat_label_all              category lable是否全部显示。取值：True、False。默认为False
                    cat_label_angle            category lable的显示倾斜度。取值：[0, 90]。默认为30
                    margin-left                该item的左间距。取值：整数。正数增加间距，负数缩小间距。默认为0
                    margin-right               该item的右间距。取值：整数。正数增加间距，负数缩小间距。默认为0
                    margin-up                  该item的上间距。取值：整数。正数增加间距，负数缩小间距。默认为0
                    margin-bottom              该item的下间距。取值：整数。正数增加间距，负数缩小间距。默认为0
                    invalid                    是否无效。取值：True、False。默认为False。当设为True时，该item不显示。默认为False
                /[item_name3]									
                                                    
                [item_name4]									
                    type                       bar_chart。该item为柱状图。必填项
                    rect                       该item的绘画区域。格式：[x, y, width, height]。该坐标相对于page的rect而言。必填项
                    data                       柱状图的数据。格式：[(数据集1), (数据集2), …]。必填项
                    bar_style                  柱状图的style。取值：vertical、horizontal。horizontal是水平柱状图，vertical是垂直柱状图。必填项
                    main_title                 主标题的内容
                    main_title_font_name       主标题的字体名称。默认为SimSun
                    main_title_font_color      主标题的字体颜色。格式：Color(r, g, b, a)，r、g、b和a的取值范围：[0, 1]。默认为黑色Color(0, 0, 0, 1)
                    main_title_font_size       主标题的字体大小。默认为10
                    x_desc                     x轴的描述信息。默认为空
                    y_desc                     y轴的描述信息。默认为空
                    legend_names               legend的名称。和data一一对应，格式：[数据集1的名称, 数据集2的名称, …]。默认为空
                    legend_position            legend的位置。取值：top-left、top-middle、top-right、bottom-left、bottom-middle、bottom-right。默认为top-right
                    legend_adjust_x	           调整legend在X轴方向的位置。取值：整数。默认为0
                    legend_adjust_y	           调整legend在Y轴方向的位置。取值：整数。默认为0
                    step_count                 Value轴的数值格数。取值：正整数。默认为4
                    cat_label_all              category lable是否全部显示。取值：True、False。默认为False
                    cat_label_angle            category lable的显示倾斜度。取值：[0, 90]。默认为30
                    style                      bar的style。取值：parallel、stacked。默认为parallel
                    label_format               bar label的格式。如，%s表示显示每个bar的数值。默认不显示
                    margin-left                该item的左间距。取值：整数。正数增加间距，负数缩小间距。默认为0
                    margin-right               该item的右间距。取值：整数。正数增加间距，负数缩小间距。默认为0
                    margin-up                  该item的上间距。取值：整数。正数增加间距，负数缩小间距。默认为0
                    margin-bottom              该item的下间距。取值：整数。正数增加间距，负数缩小间距。默认为0
                    invalid                    是否无效。取值：True、False。默认为False。当设为True时，该item不显示。默认为False
                /[item_name4]									
                                                    
                [item_name5]									
                    type                       pie_chart。该item为饼图。必填项
                    rect                       该item的绘画区域。格式：[x, y, width, height]。该坐标相对于page的rect而言。必填项
                    data                       饼图的数据。格式：[数值1, 数值2, …]。必填项
                    legend_names               legend的名称。和data一一对应，格式：[数据1的名称, 数据2的名称, …]。默认为空
                    main_title                 主标题的内容
                    main_title_font_name       主标题的字体名称。默认为SimSun
                    main_title_font_color      主标题的字体颜色。格式：Color(r, g, b, a)，r、g、b和a的取值范围：[0, 1]。默认为黑色Color(0, 0, 0, 1)
                    main_title_font_size       主标题的字体大小。默认为10
                    margin-left                该item的左间距。取值：整数。正数增加间距，负数缩小间距。默认为0
                    margin-right               该item的右间距。取值：整数。正数增加间距，负数缩小间距。默认为0
                    margin-up                  该item的上间距。取值：整数。正数增加间距，负数缩小间距。默认为0
                    margin-bottom              该item的下间距。取值：整数。正数增加间距，负数缩小间距。默认为0
                    invalid                    是否无效。取值：True、False。默认为False。当设为True时，该item不显示。默认为False
                /[item_name5]									
            /items										
        /page0											
        page1											
            ……										
        /page1											
        ……											
    /pages												
/pdf													
```

## 2 代码示例
```python
from pdflib.PDFTemplateR import PDFTemplateR

try:
    # 根据模板生成对象
    pdf = PDFTemplateR("templates/template1.xml")
    
    # 设置相关数据
    pdf.set_item_data(0, "description", content="Test Paragraph")
    pdf.set_item_data(0, "line_chart1", data=[(1, 2, 3)])
    pdf.set_item_data(0, "bar_chart1", data=[(1, 2, 3)])
    pdf.set_item_data(0, "pie_chart1", data=[1, 2, 3])
    # ......
    
    # 生成PDF文件
    pdf.draw()
except Exception as err:
    import traceback
    traceback.print_exc()
    print(err)
```
