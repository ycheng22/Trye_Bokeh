# -*- coding: utf-8 -*-
"""
Created on Mon Oct  4 00:32:49 2021

@author: Yunpeng Cheng

@E_mail: ycheng22@hotmail.com

@Github: https://github.com/ycheng22

Reference:
"""
import pandas as pd
import numpy as np

from bokeh.io import show, output_notebook, output_file
from bokeh.plotting import figure

from bokeh.models import HoverTool, ColumnDataSource, Panel, CustomJS, Column, Row
from bokeh.models import CheckboxGroup, Slider, RangeSlider, Tabs

from bokeh.palettes import Category20_16

def histogram_tab(flights):
    def make_dataset(carrier_list, range_start = -60, range_end = 120, bin_width = 5):

        by_carrier = pd.DataFrame(columns=['proportion', 'left', 'right', 
                                           'f_proportion', 'f_interval',
                                           'name', 'color'])
        range_extent = range_end - range_start
    
        # Iterate through all the carriers
        for i, carrier_name in enumerate(carrier_list):
    
            # Subset to the carrier
            subset = flights[flights['name'] == carrier_name]
    
            # Create a histogram with 5 minute bins
            arr_hist, edges = np.histogram(subset['ArrDelay'], 
                                           bins = int(range_extent / bin_width), 
                                           range = [range_start, range_end])
    
            # Divide the counts by the total to get a proportion
            arr_df = pd.DataFrame({'proportion': arr_hist / np.sum(arr_hist), 'left': edges[:-1], 'right': edges[1:] })
    
            # Format the proportion 
            arr_df['f_proportion'] = ['%0.5f' % proportion for proportion in arr_df['proportion']]
    
            # Format the interval
            arr_df['f_interval'] = ['%d to %d minutes' % (left, right) for left, right in zip(arr_df['left'], arr_df['right'])]
    
            # Assign the carrier for labels
            arr_df['name'] = carrier_name
    
            # Color each carrier differently
            arr_df['color'] = Category20_16[i]
    
            # Add to the overall dataframe
            by_carrier = by_carrier.append(arr_df)
    
        # Overall dataframe
        by_carrier = by_carrier.sort_values(['name', 'left'])
    
        return ColumnDataSource(by_carrier)
    
    def style(p):
        # Title 
        p.title.align = 'center'
        p.title.text_font_size = '20pt'
        p.title.text_font = 'serif'
    
        # Axis titles
        p.xaxis.axis_label_text_font_size = '14pt'
        p.xaxis.axis_label_text_font_style = 'bold'
        p.yaxis.axis_label_text_font_size = '14pt'
        p.yaxis.axis_label_text_font_style = 'bold'
    
        # Tick labels
        p.xaxis.major_label_text_font_size = '12pt'
        p.yaxis.major_label_text_font_size = '12pt'
    
        return p
    
    def make_plot(data):
        # Blank plot with correct labels
        p = figure(plot_width = 700, plot_height = 700, 
                  title = 'Histogram of Arrival Delays by Carrier',
                  x_axis_label = 'Delay (min)', y_axis_label = 'Proportion')
    
        # Quad glyphs to create a histogram
        p.quad(source = data, bottom = 0, top = 'proportion', left = 'left', right = 'right',
               color = 'color', fill_alpha = 0.7, hover_fill_color = 'color', legend_field = 'name',
               hover_fill_alpha = 1.0, line_color = 'black')
    
        # Hover tool with vline mode
        hover = HoverTool(tooltips=[('Carrier', '@name'), 
                                    ('Delay', '@f_interval'),
                                    ('Proportion', '@f_proportion')],
                          mode='vline')
    
        p.add_tools(hover)
    
        # Styling
        p = style(p)
    
        return p
    
    # Available carrier list
    available_carriers = list(flights['name'].unique())
    
    # Sort the list in-place (alphabetical order)
    available_carriers.sort()
    
    #make dataset
    carrier_list=available_carriers
    data = make_dataset(carrier_list, range_start = -60, range_end = 120, bin_width = 5)
    
    
    source = ColumnDataSource(dict(proportion = [], left = [], right = [], color=[], name=[], f_proportion=[], f_interval=[]))

    callback = CustomJS(args = {'source': source, 'data_source': data},
        code = """
            var data = data_source.data;
            var s_data = source.data;
    
            var select_vals = cb_obj.active.map(x => cb_obj.labels[x]);
            console.log(select_vals);
            //read original data
    
            var proportion_data = data['proportion'];
            var left_data = data['left'];
            var right_data = data['right'];
            var color_data = data['color'];
            var name_data = data['name'];
            var f_proportion_data = data['f_proportion'];
            var f_interval_data = data['f_interval'];
    
    
            //initialize source data
            var proportion = s_data['proportion'];
            proportion.length = 0;
            var left = s_data['left'];
            left.length = 0;
            var right = s_data['right'];
            right.length = 0;
            var color = s_data['color'];
            color.length = 0;
            var name = s_data['name'];
            name.length = 0;
            var f_proportion = s_data['f_proportion'];
            f_proportion.length = 0;
            var f_interval = s_data['f_interval'];
            f_interval.length = 0;
    
            for (var i = 0; i < proportion_data.length; i++) {
                if (select_vals.indexOf(name_data[i]) >= 0) {
                    proportion.push(proportion_data[i]);
                    left.push(left_data[i]);
                    right.push(right_data[i]);
                    color.push(color_data[i]);
                    name.push(name_data[i]);
                    f_proportion.push(f_proportion_data[i]);
                    f_interval.push(f_interval_data[i]);
                    }
            }
            source.change.emit();
            console.log("callback completed");
        """)
    
    p = make_plot(source)
    
    chkbxgrp = CheckboxGroup(labels = available_carriers, active=[])
    chkbxgrp.js_on_change('active', callback)
    
    range_slider = RangeSlider(start = -60, end = 180, value = (-60, 120), step = 5, title = 'Delay Range (min)')
    range_slider.js_on_change('value',
        CustomJS(args=dict(other=p.x_range),
                 code="""
                 other.start = this.value[0];
                 other.end = this.value[1];
                 """)
    )
    
    layout = Row(Column(chkbxgrp, range_slider), p)
    
    tab = Panel(child=layout, title = 'Delay Histogram')
    
    return tab