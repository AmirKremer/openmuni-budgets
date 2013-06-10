define([
    'uijet_dir/uijet',
    'resources',
    'controllers/SearchedList'
], function (uijet, resources) {

    uijet.declare([{
        type    : 'Pane',
        config  : {
            element     : '#nodes_list_container',
            dont_wake   : true,
            app_events  : {
                'entities_list.selected': function ($selected) {
                    this.wake({ entity_id : $selected.attr('data-id') });
                }
            }
        }
    }, {
        type    : 'List',
        config  : {
            element     : '#nodes_list_header',
            horizontal  : true,
            position    : 'top:2rem fluid',
            signals     : {
                pre_select  : function ($selected) {
                    if ( this.$selected && $selected[0] === this.$selected[0] ) {
                        this.$selected.toggleClass('desc');
                    }
                    return {
                        column  : $selected.attr('data-column'),
                        desc    : $selected.hasClass('desc')
                    };
                }
            }
        }
    }, {
        type    : 'List',
        config  : {
            element     : '#nodes_list',
            mixins      : ['Templated', 'Scrolled'],
            adapters    : ['jqWheelScroll', 'Spin', 'SearchedList'],
            resource    : 'LatestTemplate',
            position    : 'fluid',
            search      : {
                fields  : {
                    name        : 10,
                    description : 1,
                    code        : 20
                }
            },
            sorting     : {
                name        : 'name',
                '-name'     : resources.utils.reverseSorting('name'),
                code        : 'code',
                '-code'     : resources.utils.reverseSorting('code'),
                direction   : 'direction',
                '-direction': resources.utils.reverseSorting('direction')
            },
            signals     : {
                post_init       : function () {
                    this.scope = null;
                },
                pre_wake        : function () {
                    var entity_id = this.context.entity_id;
                    if ( entity_id ) {
                        if ( this.latest_entity_id !== entity_id ) {
                            this.latest_entity_id = entity_id;
                            // this makes sure search index is rebuilt and view is re-rendered
                            this.changed = true;
                            // this makes sure the resource will execute fetch to sync with remote server
                            this.has_data = false;
                            this.scope = null;
                            this.resource.url = API_URL + 'nodes/latest/' + entity_id + '/';
                            this.filter(this.resource.roots);
                        }
                        else {
                            this.changed = false;
                        }
                    }
                    return this.changed;
                },
                pre_update      : 'spin',
                post_fetch_data : 'spinOff',
                post_render     : function () {
                    this.$children = this.$element.children();
                    this.publish('rendered');
                },
                post_wake       : function () {
                    if ( this.changed ) {
                        this.index()
                            .search_index.add( this.resource.byAncestor(this.scope) );
                        this.publish('ready', this.context);
                    }
                },
                pre_select      : function ($selected) {
                    return ! $selected[0].hasAttribute('data-leaf') && +$selected.attr('data-id');
                },
                post_select     : function ($selected) {
                    var node_id = +$selected.attr('data-id') || null;
                    // make sure we rebuild index and re-render
                    this.changed = true;
                    this.scope = node_id || null;
                    this.filter(this.resource.byParent, node_id)
                        .wake(true);
                }
            },
            app_events  : {
                'nodes_search.changed'                      : 'filterItems+',
                'nodes_search.exited'                       : function (query) {
                    if ( ! query ) {
                        this.changed = true;
                        this.filter(this.resource.byParent, this.scope)
                            .wake(true);
                    }
                },
                'nodes_list.filtered'                       : 'scroll',
                'filters_search.clicked'                    : function () {
                    this.changed = true;
                    this.filter(this.resource.byAncestor, this.scope)
                        .wake(true);
                },
                'node_breadcrumb_main.clicked'              : function () {
                    this.changed = true;
                    this.scope = null;
                    this.wake('roots');
                },
                'node_breadcrumb_back.clicked'              : function (data) {
                    var scope = data.context.id;
                    this.changed = true;
                    this.scope = scope;
                    this.filter(this.resource.byParent, scope)
                        .wake(true);
                },
                'nodes_breadcrumbs.selected'                : 'post_select+',
                'nodes_breadcrumbs_history_menu.selected'   : 'post_select+',
                'nodes_list_header.selected'                : function (data) {
                    this.sort((data.desc ? '-' : '') + data.column);
                    this.changed = true;
                    this.wake(true);
                }
            }
        }
    }]);

});
