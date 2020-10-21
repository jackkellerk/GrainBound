# imports packages
import numpy as np
import pandas as pd
from functools import partial
from bokeh.layouts import gridplot
from bokeh.models import BoxSelectTool, LassoSelectTool, ColumnDataSource, Button
from bokeh.plotting import curdoc, figure
from bokeh.events import Reset
from bokeh.io.export import get_screenshot_as_png

from bokeh.models import Div
div = Div(text="<img src='https://static.wixstatic.com/media/eedfcd_802a6f5ed359490a9e0196ac5d32a692~mv2.png/v1/fill/w_315,h_314,al_c,q_85,usm_0.66_1.00_0.01/GrainBound-graphic-3.webp'>", width=25, height=25, sizing_mode='fixed')


# reads the files
df = pd.read_pickle('Data_out')

# Corrections for products made

# This removes extra spaces
df['Product Goal'] = df['Product Goal'].replace({'B ':'B', 'A ':'A', 'C ':'C', np.nan:'N', 0:'Za', 1:'Zb', -100:'nan'})

# This removes extra spaces
df['Product Made'] = df['Product Made'].replace({'B ':'B', 'A ':'A', 'C ':'C', np.nan:'N',  -100:'nan'})

#Builds dicts for the products
Product_goal_dict = dict(enumerate(df['Product Goal'].astype('category').cat.categories))
Product_made_dict = dict(enumerate(df['Product Made'].astype('category').cat.categories))

# Corrections for products made

# This removes extra spaces
df['Product Goal'] = df['Product Goal'].replace({'B ':'B', 'A ':'A', 'C ':'C', np.nan:'z_nan', 0:'z_a', 1:'z_b', -100:'znan'})

# This removes extra spaces
df['Product Made'] = df['Product Made'].replace({'B ':'B', 'A ':'A', 'C ':'C', np.nan:'z_nan',  -100:'z_nan'})

# Sets this up as a catagorical value
df['Product Goal Catagorical'] = df['Product Goal'].astype('category').cat.codes

# Sets this up as a catagorical value
df['Product Made Catagorical'] = df['Product Made'].astype('category').cat.codes

# sets the tools that are available
TOOLS = "pan,wheel_zoom,box_select,lasso_select,reset, save"

# defines the line style
LINE_ARGS = dict(color="#3A5785", line_color=None)

# initialize the selected dictionary
selected_dict = {}

nbins_ = 200
nbins = nbins_

# function that creates the histogram
def create_histogram(df, y_label=None, nbins=nbins, selected_dict = selected_dict):

    # extracts data from the y_label extracted
    data = df[y_label]

    if 'Catagorical' in y_label:
        nbins = len(np.unique(data))
    else:
        nbins = 200

    vhist, vedges = np.histogram(data, bins=nbins)

    # builds a zero vector
    vzeros = np.zeros(len(vedges) - 1)
    vmax = max(vhist) * 1.1

    # builds the figures
    pv = figure(toolbar_location='above', plot_width=150, plot_height=300, x_range=(-vmax, vmax),
                min_border=10, y_axis_location="right", tools=TOOLS)

    # sets the gridline
    pv.ygrid.grid_line_color = None

    # tilts the label orientation
    pv.xaxis.major_label_orientation = np.pi / 4

    # sets the background fill color
    pv.background_fill_color = "#fafafa"

    # constructs the data for plotting histograms with quad
    data = {'top': vedges[1:], 'bottom': vedges[:-1], 'left': vzeros, 'right': vhist}

    # builds the data source from the data
    source = ColumnDataSource(data)

    # Plots the original graph
    pv.quad(top="top", bottom="bottom", left="left", right="right", source=source, color="white", line_color="#3A5785",line_width = .1)

    # plots the negative and positive of the results
    vh1 = pv.quad(left=0, bottom=vedges[:-1], top=vedges[1:], right=vzeros, alpha=0.5, **LINE_ARGS)
    vh2 = pv.quad(left=0, bottom=vedges[:-1], top=vedges[1:], right=vzeros, alpha=0.1, **LINE_ARGS)

    # adds the axis and removes my label from the data
    pv.yaxis.axis_label = y_label.split('_')[0]

    if 'Catagorical' in y_label:
        name = y_label.split(' Catagorical')[0]
        y_tick = np.arange(len(np.unique(df[name]))) + .5

        cat = df[name].astype('category').cat.categories
        string = []

        for cat_ in cat:
            new_string = cat_.replace('z_', '').replace('a', '0').replace('b', '1').replace('n0n', 'nan')

            string.append(new_string)
        pv.yaxis.ticker = y_tick
        pv.yaxis.major_label_overrides = dict(zip(y_tick, string))



    # callback for when we select some data
    source.selected.on_change('indices', partial(callback, y_label=y_label,
                                                 main=main, df=df, sources=sources,
                                                 selected_dict=selected_dict,
                                                 vh1_list=vh1_list, vh2_list=vh2_list,
                                                 nbins=nbins))
    # callback for the reset operation
    selected_dict = pv.on_event('reset', partial(reset, selected_dict=selected_dict, df =df , vh1_list = vh1_list,
                                                 vh2_list = vh2_list, nbins=nbins))

    return pv, vh1, vh2, vhist, vedges, source


# function that resets the dictionary to the default
def reset(selected_dict, df, vh1_list, vh2_list, nbins):
    # resets the dictionary
    selected_dict = {}
    update_graphs(df, selected_dict, vh1_list, vh2_list, nbins=nbins)
    return selected_dict

def update_graphs(df, selected_dict, vh1_list, vh2_list, nbins=nbins):
    # intializes the array so that all index are selected
    ind_selected = np.linspace(0, df.shape[0] - 1, df.shape[0]).astype(int)

    # loops around the selection dictionary
    for selected in selected_dict:

        if 'Product' in selected:
            nbins_ = len(np.unique(df[selected]))
        else:
            nbins_ = 200

        # computes the histogram
        #vhist, vedges = np.histogram(df[selected], bins=nbins_)
        # vzeros = np.zeros(len(vedges) - 1)
        # vmax = max(vhist) * 1.1

        # builds a temporary index vector for index
        temp_ind = []

        # loops around all of the selections for a single parameter
        for index_value in selected_dict[selected]:
            vhist, vedges = np.histogram(df[selected], bins=nbins_)
            lower_bound = vedges[index_value]
            upper_bound = vedges[index_value + 1]

            # Appends all the selections to a dictionary
            temp_ind = np.append(temp_ind,
                                 np.where(
                                     np.logical_and(
                                         df[selected] >= lower_bound,
                                         df[selected] <= upper_bound))).astype(int)

        # computes the index that remain in selected
        ind_selected = np.intersect1d(ind_selected, temp_ind)

    # this calls a function that plots the secondary graphs
    add_secondary_plots(df, ind_selected, vh1_list, vh2_list, nbins_)

def add_secondary_plots(df, ind_selected, vh1_list, vh2_list, nbins):

    # finds the columns that we want to plot
    cols = df.columns.str.contains('_update') + df.columns.str.contains('Catagorical')

    # loops around the selected parameters
    for i, selected in enumerate(df.columns[cols]):

        if 'Product' in selected:
            nbins = len(np.unique(df[selected]))
        else:
            nbins = 200

        #computes the original hisogram
        vhist, vedges = np.histogram(df[selected], bins=nbins)

        # Checks if the number of selected values are 0 or all
        if len(ind_selected) == 0 or df.shape[0] == len(ind_selected):

            # builds a 0 axis
            vzeros = np.zeros(len(vedges) - 1)

            # applies the 0 values as the histogram values
            vhist1, vhist2 = vzeros, vzeros
        else:
            # builds a ones array of the same shape as the raw data
            neg_inds = np.ones_like(df[selected], dtype=np.bool)
            # sets the selected values equal to false
            neg_inds[ind_selected] = False
            # computes the histogram for the negative and positive values based on the selection and the original histogram
            vhist1, _ = np.histogram(df[selected][ind_selected], bins=vedges)
            vhist2, _ = np.histogram(df[selected][neg_inds], bins=vedges)

        # updates the data in the histograms
        vh1_list[i].data_source.data["right"] = vhist1
        vh2_list[i].data_source.data["right"] = -vhist2


def callback(attr, old, new, y_label, main, df, sources, selected_dict, vh1_list, vh2_list, nbins=nbins):
    # finds the columns we are interested in
    ind = df.columns.str.contains('_update') + df.columns.str.contains('Catagorical')

    # finds the index of the catagories we just changed
    selected_cat = np.argwhere(df.columns[ind] == y_label).squeeze()

    assert (y_label == df.columns[ind][selected_cat])

    # function that builds a dictionary of the selected values
    selected_dict[y_label] = new

    # This checks to see if there are selected values saved
    if len(selected_dict.keys()) != 0:
        update_graphs(df, selected_dict, vh1_list, vh2_list, nbins=nbins)


# selects only the columns we want to plot based on the names
ind = df.columns.str.contains('_update') + df.columns.str.contains('Catagorical')


# builds arrays of all the information we want to save
main = []
vh1_list = []
vh2_list = []
vhist = []
vedges = []
sources = []
for columns in df.columns[ind]:
    main_, vh1_, vh2_, vhist_, vedges_, source_ = create_histogram(df, columns, nbins=nbins, selected_dict=selected_dict)
    main.append(main_)
    vh1_list.append(vh1_)
    vh2_list.append(vh2_)
    vhist.append(vhist_)
    vedges.append(vedges_)
    sources.append(source_)

# This adds a blank value at the end to flatten
main.append(div)
vh1_list.append(None)
vh2_list.append(None)
vhist.append(None)
vedges.append(None)

# sets the graph layout
layout = gridplot([main[0:6], main[6:12], main[12:18], main[18:24], main[24:30]])

#image = get_screenshot_as_png(layout)#, height=2400, width=2400, driver=webdriver)


curdoc().add_root(layout)
