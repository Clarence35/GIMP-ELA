#!/usr/bin/env python

# The MIT License (MIT)
# Copyright (c) 2012-2013 Alfredo Torre
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

# Error level analysis (ELA) shows differing error levels throughout an image,
# strongly suggesting some form of digital manipulation.
# ELA works by intentionally resaving the image at a known error rate.

from gimpfu import *
import os, sys, webbrowser
from datetime import datetime

plugin_version = 1.1

# create an output function that redirects to gimp's Error Console
def gprint( msg ):
    pdb.gimp_message(msg)
    return

## Print a HTML report.
def html_report(i, q, reportFile = "test.html") :
    htmFile = open(reportFile, "w")
    htmFile.write("""
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
        "http://www.w3.org/TR/html4/loose.dtd">
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html;charset=ISO-8859-1">
        <link rel="stylesheet" href="http://www.w3.org/StyleSheets/Core/Modernist" type="text/css">
        <title>GIMP Error Level Analysis Report</title>
    </head>
    <body>
        <h1>GIMP forensic analysis report</h1>
        <p>This is an automated report generated by the
        <a href="http://www.gimp.org/" target="_blank">GIMP</a> ELA forensic plugin on
        <b>""")
    adesso = datetime.now()
    htmFile.write(adesso.strftime("%m/%d/%Y") + "</b> at <em>")
    htmFile.write(adesso.strftime("%H:%M")+ "</em>.</p>")
    # Print information about analyzed image
    htmFile.write("<h2>Image information</h2>")
    htmFile.write("<dl>")
    htmFile.write("<dt>Image name</dt>")
    htmFile.write("<dd>"+ i.filename +"</dd>")

    htmFile.write("<dt>Image width</dt>")
    htmFile.write("<dd>"+ str(i.width) +"</dd>")
    htmFile.write("<dt>Image height</dt>")
    htmFile.write("<dd>"+ str(i.height) +"</dd>")

    htmFile.write("<dt>Quality of resaved JPEG image</dt>")
    htmFile.write("<dd>"+ str(q) +"</dd>")

    htmFile.write("</dl>")
    # Print Version and date information
    htmFile.write("<h2>Version information</h2>")
    htmFile.write("<dl>")
    htmFile.write("<dt>GIMP version</dt>")
    htmFile.write("<dd>"+ str(gimp.pdb.gimp_version()) +"</dd>")
    htmFile.write("<dt>JPEG ELA plugin version</dt>")
    htmFile.write("<dd>"+ str(plugin_version) +"</dd>")
    htmFile.write("</dl>")

    htmFile.write("""
    <h3>Reference</h3>
    <h4>JPEG Error Level Analysis</h4>
    <p>
    <i>Error Level Analysis</i> (<acronym>ELA</acronym>) identifies areas within an image that are at different compression levels. With <a href="http://en.wikipedia.org/wiki/JPEG" target="_blank" title="Wikipedia definition">JPEG</a> images, the entire picture should be at roughly the same error level. If a section of the image is at a significantly different error level, then it likely indicates a digital modification.
    </p>
    <p>
    JPEG images use a lossy compression system. Each re-encoding (resave) of the image adds more quality loss to the image. Specifically, the JPEG algorithm operates on an 8x8 pixel grid. Each 8x8 square is compressed independently. If the image is completely unmodified, then all 8x8 squares should have similar error potentials. If the image is unmodified and resaved, then every square should degrade at approximately the same rate.

ELA saves the image at a specified JPEG quality level. This resave introduces a known amount of error across the entire image. The resaved image is then compared against the original image.

If an image is modified, then every 8x8 square that was touched by the modification should be at a higher error potential than the rest of the image. Modified areas will appear with a higher potential error level.
    </p>
    <p>JPEG stores colors using the <acronym><a href="http://en.wikipedia.org/wiki/YUV" target="_blank" title="Wikipedia definition">YUV</a></acronym> color space. 'Y' is the luminance, or gray-scale intensity of the image, 'U' and 'V' are the chrominance-blue and chrominance-red color portions. For displaying, the JPEG decoder converts the image from YUV to RGB.

JPEG always encodes luminance with an 8x8 grid. However, chrominance may be encoded using 8x8, 8x16, 16x8, or 16x16. The chrominance subsampling is a JPEG encoding option. Depending on the selected chrominance subsampling, each 8x8, 8x16, 16x8, 16x16 grid will be independently encoded.</p>
    <h5>Analysis</h5>
    <p>With ELA, every grid that is not optimized for the quality level will show grid squares that change during a resave. For example, digital cameras do not optimize images for the specified camera quality level (high, medium, low, etc.). Original pictures from digital cameras should have a high degree of change during any resave (high ELA values). However, an unmodified digital photo that has been resaved will have lower ELA values. In contrast, if the grid square is already at its minimum error level, then it will not change during the resave.</p><p class="ltb">&nbsp;</p>
    <h2>Authors of the plugin</h2>
    <dl>
        <dt>Alfredo Torre</dt>
        <dd><a href="https://twitter.com/skydiamond">@skydiamond</a></dd>
    </dl>

    <address>
        Department of Electrical, Electronic and Computer Engineering. University of Catania, Italy.<br>
        <a href="http://www.dieei.unict.it/">www.dieei.unict.it</a>
    </address>

    """)
    htmFile.write("""</body></html>""")
    htmFile.close
    webbrowser.open(reportFile, new=2)
    return


def error_level_analysis(img, quality, report, reportFile) :
    g = gimp.pdb
    #<M-T-F2>img = gimp.image_list()[0]
    layers = img.layers
    tmpfile = "error-level-analysis-tmp.jpg"
    if (img.filename == None) :
        gprint("Error. The image must be stored before applying ELA.")
        return
    gimp.progress_init("Analyzing error levels on " + img.filename )

    # Separate contectual changes (brush, colors, etc.) from the user
    gimp.context_push()
    # Allow all these changes to apprear as 1 atomic action (1 undo)
    img.undo_group_start()

    # Set up an undo group, so the operation will be undone in one step.
    #g.gimp_undo_push_group_start(img)  # DEPRECATED

    # Creating a temporary image from the current one
    img_tmp = g.gimp_image_duplicate(img)
    # Merge the layers which are visible into a single layer
    # The final layer is large enough to contain all of the merged layers.
    g.gimp_image_merge_visible_layers(img_tmp, EXPAND_AS_NECESSARY)
    # get the current drawable ID, because the img-tmp is in a new layer
    draw_tmp = g.gimp_image_get_active_drawable(img_tmp)
    g.file_jpeg_save(img_tmp, draw_tmp, tmpfile, tmpfile, quality, 0, 0, 0, "GIMP ELA Temporary Image", 0, 0, 0, 0)
    draw_tmp = g.gimp_file_load_layer(img_tmp, tmpfile)
    # create new layer; syntax  image layer parent_layer position
    #g.gimp_image_insert_layer(img_tmp, draw_tmp, 0, -1)
    img_tmp.add_layer(draw_tmp, 0)
    # Set the combination mode of the specified layer.
    # syntax: lager combination_mode.
    # absolute value of the difference between the highest layer and the one immediately below.
    g.gimp_layer_set_mode(draw_tmp, DIFFERENCE_MODE)
    os.remove(tmpfile)
    g.gimp_edit_copy_visible(img_tmp)
    error_layer = g.gimp_layer_new_from_visible(img_tmp, img_tmp, "Error Levels")
    #g.gimp_image_insert_layer(img_tmp, error_layer, 0, -1)
    img_tmp.add_layer(error_layer, 0)
    # Automatically modifies intensity levels in the specified drawable(layer)
    g.gimp_levels_stretch(error_layer)
    # Only for testing purposes
    #g.gimp_display_new(img_tmp)

    # ADD ERROR LEVELS AS A NEW LAYER ON THE ORIGINAL IMAGE
    g.gimp_edit_copy_visible(img_tmp)
    # Create and return a new layer from what is visible in an image. source_img dest_img
    error_layer = g.gimp_layer_new_from_visible(img_tmp, img, "Error Levels")
    img.add_layer(error_layer, 0)
    if(report) :
        if(reportFile != None) :
            html_report(img, quality, reportFile)
        else :
            html_report(img, quality)
    # Finish the undo group.
    #g.gimp_undo_push_group_end(img) # DEPRECATED

    # Leave the user in the same context they were in before
    img.undo_group_end()
    # Return the user to the context they were in before
    gimp.context_pop()

    # Flush all internal changes to the user interface
    # g.gimp_displays_flush
    return



register(
    "python_fu_error_level_analysis",
    "JPEG Error Level Analysis. Set the quality of the resaved JPEG image between 0 and 1 to calculate the difference layer. Therefore, you could choose to produce a HTML record file in your " +
    " user's home directory.",
    "JPEG Error level analysis (ELA) shows differing error levels throughout an image,  strongly suggesting some form of digital manipulation.",
    "Alfredo Torre",
    "Alfredo Torre",
    "September 2012",
    "JPEG ELA",
    "*",      # Alternately use RGB, RGB*, GRAY*, INDEXED etc.
    [
        (PF_IMAGE,    "img",      "Input image",      None),
        (PF_SLIDER, "quality",  "_Quality", 0.7, (0, 1, 0.1)),
        (PF_BOOL, "report", "Create HTML report", True),
        (PF_STRING, "reportName", "R_eport name", "Report_JPEG_ELA.html")

    ],
    [],
    error_level_analysis,
    menu="<Image>/Filters/Forensics"
    )

main()
