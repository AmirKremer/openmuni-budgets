define([
    'uijet_dir/uijet',
    'api',
    'common_resources',
    'backbone-fetch-cache'
], function (uijet, api, resources) {

    function sortByPeriodstart (a, b) {
        return new Date(a.get(period_start)) > new Date(b.get(period_start)) ? 1 : -1;
    }

    /**
     * Gets the latest context that has a `period_start` that precedes the period
     * or is equal to it.
     * 
     * This function has a side-effect of reducing `contexts` by shifting items
     * if their preceding item's `period_start` is before `period`.
     * 
     * @param {Array} contexts - list of Context model instances
     * @param {String} period - a string representation of a date
     * @returns {Object|undefined} - latest context to use for this period's series
     */
    function latestContextForPeriod (contexts, period) {
        var context, period_to_date;
        if ( contexts.length ) {
            if ( contexts.length === 1 ) {
                context = contexts[0];
            }
            else {
                period_to_date = new Date(period.toString());
                context = contexts[0];
                if ( new Date(context.get(period_start)) <= period_to_date &&
                     new Date(contexts[1].get(period_start)) <= period_to_date ) {
    
                    contexts.shift();
                    return latestContextForPeriod(contexts, period);
                }
            }
        }
        return context;
    }

    var period_start = 'period_start',
        reverseSorting = function (field) {
            return function (a, b) {
                var a_val = a.get(field),
                    b_val = b.get(field);
                return a_val < b_val ?
                    1 :
                    a_val > b_val ?
                        -1 :
                        0;
            };
        },
        nestingSortFactory = function (reverse) {
            var a_is_smaller = reverse ? 1 : -1,
                a_is_bigger = reverse ? -1 : 1;
                
            return function (a, b) {
                var a_attrs = a.attributes,
                    b_attrs = b.attributes,
                    a_ancestors = a_attrs.ancestors,
                    b_ancestors = b_attrs.ancestors,
                    n = 0, m = 0, 
                    a_top = a_attrs, b_top = b_attrs,
                    go_deeper = true,
                    a_code, b_code;
    
                do {
                    if ( a_ancestors[n] ) {
                        a_top = a_ancestors[n];
                        n += 1;
                    }
                    else {
                        go_deeper = false;
                        a_top = a_attrs;
                    }
                    if ( b_ancestors[m] ) {
                        b_top = b_ancestors[m];
                        m += 1;
                    }
                    else {
                        go_deeper = false;
                        b_top = b_attrs;
                    }
                }
                while ( go_deeper && a_top.id === b_top.id );
    
                a_code = a_top.code;
                b_code = b_top.code;
    
                // if `a` and `b` are not in same depth
                return a_code == b_code ?
                    // check if `a` is higher in the hierarchy, otherwise `b` is
                    a_top === a_attrs ?
                        a_is_smaller : a_is_bigger :
                    // if they are in same depth order by code
                    a_code < b_code ? a_is_smaller : a_is_bigger;
            };
        },
        /*
         * Muni (Entity) Model
         */
        Muni = uijet.Model(),
        /*
         * Munis (Entities) Collection
         */
        Munis = uijet.Collection({
            model   : Muni,
            url     : function () {
                return api.getRoute('entities');
            },
            parse   : function (response) {
                //! Array.prototype.filter
                return response.results;
            }
        }),
        /*
         * TemplateNode Model
         */
        Node = uijet.Model({
            branchName  : function (from_id) {
                var ancestors = this.attributes.ancestors,
                    index = from_id ? 0 : null,
                    result = [],
                    ancestors_len = ancestors.length;

                if ( index !== null ) {
                    ancestors.some(function (ancestor) {
                        if ( ancestor.id === from_id ) {
                            return true
                        }
                        index++;
                        return false;
                    });
                    index += 1;
                }

                while ( ancestors_len > index ) {
                    ancestors_len -= 1;
                    result.unshift(ancestors[ancestors_len].name);
                }

                return result;
            },
            commas      : function () { 
                return function (text, render) {
                    return uijet.utils.formatCommas(render(text));
                };
            }
        }),
        /*
         * TemplateNodes Collection
         */
        Nodes = uijet.Collection({
            model       : Node,
            url         : function () {
                return api.getRoute('templateNodes');
            },
            comparator  : function (a, b) {
                var a_attrs = a.attributes,
                    b_attrs = b.attributes,
                    diff = a_attrs.depth - b_attrs.depth;
                if ( ! diff ) {
                    diff = a_attrs.code < b_attrs.code;
                    return diff ?
                        -1 :
                        a_attrs.code > b_attrs.code ?
                            1 :
                            0;
                }
                return diff > 0 ? 1 : -1;
            },
            /**
             * Setting `ancestors` array of `id`s, `leaf_node` boolean flag
             * 
             * @param {Object|Array} response
             * @returns {Object|Array} response
             */
            parse       : function (response) {
                var results = response.results || response,
                    last = results.length - 1,
                    node, n, parent, state;
                /* 
                 * init `ancestor` to `[]`
                 * if no `children` or it's empty set `leaf_node` to `true`
                 */
                for ( n = last; node = results[n]; n-- ) {
                    node.ancestors || (node.ancestors = []);

                    if ( ! (node.children && node.children.length) ) {
                        node.leaf_node = true;
                    }

                    if ( parent = node.parent ) {
                        node.parent = parent.id || parent;

                        if ( ! ('selected' in node) ) {
                            if ( state = this.get(node.parent).get('selected') ) {
                                node.selected = state;
                            }
                        }
                    }
                }

                return results;
            },
            roots       : function () {
                return this.byParent(null);
            },
            byParent    : function (parent_id) {
                return this.where({
                    parent  : parent_id
                });
            },
            byAncestor  : function (ancestor_id) {
                if ( ancestor_id ) {
                    return this.filter(function (node) {
                        return node.attributes.ancestors.some(function (ancestor) {
                            return ancestor.id === ancestor_id;
                        });
                    });
                }
                else {
                    return this.models;
                }
            },
            branch      : function (node_id) {
                var tip_node, branch;
                if ( node_id ) {
                    tip_node = this.get(node_id);
                    //! Array.prototype.map
                    branch = tip_node.get('ancestors')
                        .map( function (ancestor_id) {
                            return this.get(ancestor_id);
                        }, this );
                    branch.push(tip_node);
                }
                return branch || [];
            }
        }),
        /*
         * Context Model
         */
        Context = uijet.Model(),
        /*
         * Contexts Collection
         */
        Contexts = uijet.Collection({
            model   : Context,
            entities: [],
            url     : function () {
                return api.getRoute('contexts');
            },
            parse   : function (response) {
                return response.results;
            },
            hasMunis: function (muni_ids) {
                return muni_ids.every(function (muni_id) {
                    return ~ this.entities.indexOf(muni_id);
                }, this);
            }
        }),
        /*
         * TimeSeries collection
         */
        TimeSeries = uijet.Collection({
            model           : resources.TimeSeriesModel,
            fetch           : function () {
                return uijet.whenAll(this.models.map(function (model) {
                    return model.fetch();
                }));
            },
            periods         : function () {
                return this.pluck('periods').reduce(function (prev, current) {
                    current.forEach(function (item) {
                        if ( !~ this.indexOf(item) )
                            this.push(item);
                    }, prev);
                    return prev;
                }).sort();
            },
            recalcFactors   : function () {
                var muni_ids = this.pluck('muni_id'),
                    contexts = uijet.Resource('Contexts'),
                    has_contexts = contexts.hasMunis(muni_ids),
                    dfrd;
                if ( has_contexts ) {
                    this.each(function (model) {
                        model.recalcFactor();
                    });
                }
                else {
                    return contexts.fetch({
                        data: {
                            entities: _.uniq(muni_ids.concat(contexts.entities)).toString()
                        }
                    });
                }
                dfrd = uijet.Promise();
                dfrd.resolve();
                return dfrd.promise();
            },
            extractLegend   : function () {
                return this.models.map(function (model) {
                    var attrs = model.attributes;
                    return {
                        id          : attrs.id,
                        title       : attrs.title,
                        placeholder : attrs.title || gettext('Insert title'),
                        nodes       : attrs.nodes,
                        muni        : new Muni({
                            id  : attrs.muni_id,
                            name: attrs.muni
                        }),
                        amount_type : attrs.amount_type,
                        color       : attrs.color
                    };
                });
            }
        }),
        Template = uijet.Model(),
        /*
         * Collection of NodeTemplate collections
         */
        Templates = uijet.Collection({
            model   : Template
        });

    resources.TimeSeriesModel.prototype.recalcFactor = function () {
        var normalize_by = uijet.Resource('NodesListState').get('normalize_by'),
            series = this.get('series'),
            contexts;

        if ( normalize_by ) {
            contexts = uijet.Resource('Contexts')
                .where({ entity : this.get('muni_id') });
            if ( contexts.length )
                contexts.sort(sortByPeriodstart);
        }

        //TODO: assuming here period is a "full year"
        this.get('periods').forEach(function (period) {
            if ( series[period] ) {
                var context = contexts && latestContextForPeriod(contexts, period);
                series[period].factor = context ? +context.get('data')[normalize_by] : 1;
            }
        });
    };

    resources.Munis.prototype.url = function () {
        return api.getRoute('entities');
    };

    resources.State.prototype.url = function () {
        return this.urlRoot() + (this.id ? this.id : '');
    };
    resources.State.prototype.urlRoot = function () {
        return api.getRoute('toolStates');
    };

    resources.TimeSeriesModel.prototype.url = function () {
        return api.getTimelineRoute(this.attributes.muni_id, this.attributes.nodes);
    };

    resources.Node = Node;
    resources.Nodes = Nodes;
    resources.Template = Template;
    resources.Templates = Templates;
    resources.Context = Context;
    resources.Contexts = Contexts;
    resources.TimeSeries = TimeSeries;
    resources.utils = {
        reverseSorting      : reverseSorting,
        nestingSort         : nestingSortFactory(false),
        reverseNestingSort  : nestingSortFactory(true)
    };

    return resources;
});
