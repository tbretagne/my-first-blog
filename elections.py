from spyre import server

import matplotlib.pyplot as plt
# import numpy as np
import pandas as pd
import collections as co
import os
# import seaborn as sns

# sns.set_style("dark")

# import os

# from bokeh.charts import Donut
# from bokeh.resources import INLINE
# from bokeh.resources import CDN
# from bokeh.embed import components
# from bokeh.plotting import figure  #, show, output_file, vplot

DATADIR = 'data/'
STORE = 'elections.h5'

d_plt_colors = {
    'blue': '#1f77b4',
    'orange': '#ff7f0e',
    'green': '#2ca02c',
    'red': '#d62728',
    'purple': '#9467bd',
    'brown': '#8c564b',
    'pink': '#e377c2',
    'grey': '#7f7f7f',
    'yellow': '#bcbd22',
    'cyan': '#17becf'
}


dict_reg_dep = {'Alsace-Champagne-Ardenne-Lorraine':
                ['67', '68', '08', '10', '51', '52', '54', '55', '57', '88'],
                'Aquitaine-Limousin-Poitou-Charentes':
                ['24', '33', '40', '47', '64', '19', '23', '87', '16', '17',
                 '79', '86'],
                'Auvergne-Rhône-Alpes':
                ['03', '15', '43', '63', '01', '07', '26', '38', '42', '69',
                 '73', '74'],
                'Bourgogne-Franche-Comté':
                ['21', '58', '71', '89', '25', '39', '70', '90'],
                'Bretagne':
                ['22', '29', '35', '56'],
                'Centre-Val de Loire':
                ['18', '28', '36', '37', '41', '45'],
                'Corse':
                ['2A', '2B'],
                'Ile de France':
                ['75', '77', '78', '91', '92', '93', '94', '95'],
                'Languedoc-Roussillon-Midi-Pyrénées':
                ['11', '30', '34', '48', '66', '09', '12', '31', '32', '46',
                 '65', '81', '82'],
                'Nord-Pas de Calais-Picardie':
                ['59', '62', '02', '60', '80'],
                'Normandie': ['14', '27', '50', '61', '76'],
                'Pays de la Loire':
                ['44', '49', '53', '72', '85'],
                "Provence-Alpes-Côte d'Azur":
                ['04', '05', '06', '13', '83', '84'],
                }

dict_nuance_color = co.OrderedDict(
    [('EXD', 'k'), ('MNR', 'k'), ('FRN', 'k'), ('FN', 'k'),
     ('DVD', '#1f77b4'), ('UMP', '#1f77b4'), ('MPF', '#1f77b4'),
     ('DLF', '#1f77b4'), ('UD', '#1f77b4'), ('PR', '#1f77b4'),
     ('DL', '#1f77b4'), ('RPF', '#1f77b4'), ('RPR', '#1f77b4'),
     ('MDM', '#17becf'), ('MODEM', '#17becf'), ('NouvC', '#17becf'),
     ('UC', '#17becf'), ('UDI', '#17becf'), ('PSLE', '#17becf'),
     ('UDF', '#17becf'),
     ('DIV', '#7f7f7f'), ('REG', '#7f7f7f'), ('CPNT', '#7f7f7f'),
     ('COM', '#d62728'), ('PRV', '#d62728'),
     ('PG', '#d62728'), ('FDG', '#d62728'), ('FG', '#d62728'),
     ('RDG', '#d62728'), ('LCR', '#d62728'), ('LO', '#d62728'),
     ('EXG', '#d62728'),
     ('ECO', '#2ca02c'), ('VER', '#2ca02c'),
     ('DVG', '#e377c2'), ('UG', '#e377c2'), ('PRG', '#e377c2'),
     ('SOC', '#e377c2')])

dict_nuance_color_pres = co.OrderedDict([
    ('LE PEN', 'k'),
    ('DUPONT-AIGNAN', '#1f77b4'),
    ('SARKOZY', '#1f77b4'),
    ('BAYROU', '#17becf'),
    ('MÉLENCHON', '#d62728'),
    ('POUTOU', '#d62728'),
    ('ARTHAUD', '#d62728'),
    ('JOLY', '#2ca02c'),
    ('HOLLANDE', '#e377c2'),
    ('CHEMINADE', '#e377c2')])


class FrenchElections(server.App):
    title = "French Elections Overview"
    inputs = [{"type":      "dropdown",
               "key":       "elec_key",
               "options": [{"label": "2012 Presidential - 1st Round",
                            "value": "presidential_2012_t1"},
                           {"label": "2012 Parliament - 1st Round",
                            "value": "legislatives_2012_t1"},
                           {"label": "2007 Parliament - 1st Round",
                            "value": "legislatives_2007_t1"},
                           {"label": "2002 Parliament - 1st Round",
                            "value": "legislatives_2002_t1"},
                           {"label": "1997 Parliament - 1st Round",
                            "value": "legislatives_1997_t1"},
                           {"label": "2015 Departements - 1st Round",
                            "value": "departemental_2015_t1"}],
               "label":     "Election",
               "action_id": "election_data"},

              {"type":      "checkboxgroup",
               "label":     "Grouped by",
               "options": [{"label": "Region",
                            "value": "region_grouped",
                            "checked": False}],
               "key": "region_toggle",
               "action_id": "election_data"},

              {"type":      "checkboxgroup",
               "label":     "% Votes",
               "options": [{"label": "Normalized",
                            "value": "percent_norm",
                            "checked": False}],
               "key": "percent_toggle",
               "action_id": "election_data"}]

    tabs = ["Plot", "Data"]

    outputs = [{"type":       "plot",
                "id":         "plot",
                "tab":        "Plot",
                "control_id": "election_data"},
               {"type":       "table",
                "id":         "table_id",
                "tab":        "Data",
                "control_id": "election_data"}]

    controls = [{"type":      "HIDDEN",
                 "id":        "election_plot"},
                {"type":      "HIDDEN",
                 "id":        "election_data"}]

    def getPlot(self, params):

        # get data
        d_plot = self.getData(params)

        fig = plot_elec(self.elec_code, d_plot,
                        params['percent_toggle'])

        return fig

    def getData(self, params):

        f = str(params['elec_key'])
        self.elec_code = f
        store_elec = pd.HDFStore(DATADIR+STORE)
        store_elec.open()
        df = pd.read_hdf(store_elec, f)
        store_elec.close()
        df.index = df.index.map(add_leading_zero)
        if params['region_toggle']:
            df = group_by_region(df)
            df['Region'] = df.index
        else:
            df['Departement'] = df.index

        return df


def add_leading_zero(item):
    try:
        x = '{:02}'.format(item)
    except:
        x = item
    return x


def plot_elec(elec_name, df_elec, is_perc_norm=False,
              elec_compare=None, df_compare=None):
            # get data

        fig, ax = plt.subplots(figsize=(20, 10), dpi=300)

        is_compare = (elec_compare is not None) & (df_compare is not None)

        if is_compare:
            position = 1
        else:
            position = 0.5

        plot_elec = plot_elec_base(ax, elec_name, df_elec,
                                   is_perc_norm,
                                   position=position)

        if is_compare:
            plot_compare = plot_elec_base(ax, elec_compare, df_compare,
                                          is_perc_norm,
                                          position=0)

        # set legend on the side
        if not is_compare:
            box = ax.get_position()
            ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
            ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        else:
            ax.legend().set_visible(False)

        # set labels to something readable
        labels_reg = [item.get_text().replace('-', '\n')
                      for item in ax.get_xticklabels()]
        ax.set_xticklabels(labels_reg, fontsize='small', rotation='horizontal')

        # set tiltle
        if is_compare:
            title = 'Compare - ' + elec_name + ' and ' + elec_compare
        else:
            title = elec_name
        plt.title(title, fontsize='large')

        return fig


def plot_elec_base(ax, elec_name, df_elec,
                   is_perc_norm=False,
                   position=1):

    d_plot = df_elec
    # get the right order for parties and the colors
    if elec_name[:4].lower() == 'pres':
        d_nc = dict_nuance_color_pres
    else:
        d_nc = dict_nuance_color

    l_nuance = d_plot.columns & d_nc.keys()
    l_colors = [d_nc.get(x) for x in l_nuance]

    d_plot = d_plot[l_nuance]

    # return total percentage if needed
    if is_perc_norm:
        d_plot = d_plot.div(d_plot.sum(axis=1), axis=0)
        ax.set_ylim([0, 1])

    plot_elec = d_plot.plot(kind='bar', stacked=True, ax=ax,
                            color=l_colors, position=position, width=0.35)

    return plot_elec


def group_by_region(d_plot):
    d_plot_reg = {}
    for key, values in dict_reg_dep.items():
        d_plot_reg[key] = d_plot.loc[values].sum(axis=0)
    d_plot_reg = pd.DataFrame(d_plot_reg)
    d_plot = d_plot_reg.transpose()

    return d_plot


if __name__ == '__main__':

    app = FrenchElections()

#    store_elec = pd.HDFstore(DATADIR+STORE)
#    store_elec.open()
#    elections = pd.HDFstore(DATADIR+STORE).keys()
#    start_value = elections[0]

#    app.launch(port=9093)
    app.launch(host='0.0.0.0', port=int(os.environ.get('PORT', '5000')))
