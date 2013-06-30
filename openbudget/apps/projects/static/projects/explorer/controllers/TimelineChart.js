define([
    'uijet_dir/uijet',
    'resources',
    'api'
], function (uijet, resources, api) {

    var TimeSeriesModel = uijet.Model({
        url : function () {
            return api.getTimelineRoute(this.attributes.muni_id, this.attributes.nodes);
        },
        parse   : function (response) {
            var series = {};
            response.forEach(function (item) {
                var period = +item.period;
                if ( ! (period in series) ) {
                    series[period] = {
                        budget  : +item.budget,
                        actual  : +item.actual
                    };
                }
                else {
                    series[period].budget += +item.budget;
                    series[period].actual += +item.actual; 
                }
            });
            return {
                series  : series
            };
        },
        toSeries: function () {
            var series = this.get('series'),
                actuals = [],
                budgets = [],
                period;
            for ( period in series ) {
                actuals.push({
                    period  : period,
                    amount  : series[period].actual
                });
                budgets.push({
                    period  : period,
                    amount  : series[period].budget
                });
            }
            return [actuals,budgets];
        }
    });

    uijet.Resource('TimeSeries', uijet.Collection({
        model   : TimeSeriesModel,
        fetch   : function () {
            return uijet.whenAll(this.models.map(function (model) {
                return model.fetch();
            }));
        }
    }));

    uijet.Adapter('TimelineChart', {
        set : function (legend_item_models) {
            var updated_models = legend_item_models.map(function (legend_item) {
                var muni = legend_item.get('muni'),
                    muni_id = muni.id,
                    nodes = legend_item.get('nodes'),
                    title = legend_item.get('title'),
                    muni_name = muni.get('name'),
                    model = this.resource.get(legend_item.cid),
                    now = Date.now();

                if ( model ) {
                    model.set({
                        muni_id : muni_id,
                        nodes   : nodes,
                        title   : title,
                        muni    : muni_name
                    });
                    if ( model.hasChanged() ) {
                        model.set({ updated : now });
                    }
                }
                else {
                    model = new TimeSeriesModel({
                        id      : legend_item.cid,
                        muni_id : muni_id,
                        nodes   : nodes,
                        title   : title,
                        muni    : muni_name,
                        updated : now
                    });
                }
                return model;
            }, this);

            return this.resource.reset(updated_models).fetch();
        }
    });

});
