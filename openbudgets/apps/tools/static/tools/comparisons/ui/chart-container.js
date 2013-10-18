define([
    'uijet_dir/uijet',
    'composites/Select'
], function (uijet) {

    function enableMenuButton () {
        this.spinOff().enable();
    }

    uijet.Factory('ChartMenuButton', {
        type    : 'Button',
        config  : {
            adapters    : ['Spin'],
            dont_wake   : function () {
                return ! uijet.Resource('ToolState').has('id');
            },
            spinner_options : {
                lines   : 10,
                length  : 8,
                radius  : 6,
                width   : 4
            },
            signals         : {
                pre_click   : function () {
                    this.disable().spin();
                }
            },
            app_events      : {
                state_save_failed   : enableMenuButton
            }
        }
    });

    return [{
        type    : 'Pane',
        config  : {
            element         : '#chart_section',
            mixins          : ['Transitioned', 'Layered'],
            dont_wake       : true,
            animation_type  : 'fade',
            signals         : {
                pre_wake    : 'awaken'
            },
            app_events      : {
                'picker_done.clicked'       : 'wake',
                'add_legend_cancel.clicked' : function () {
                    var has_legend_items = uijet.Resource('LegendItems').length;
                    if ( has_legend_items ) {
                        this.wake();
                    }
                    else {
                        uijet.publish('welcome');
                    }
                },
                'chart_reset'               : 'wake+'
            }
        }
    }, {
        type    : 'Button',
        config  : {
            element : '#viz_new'
        }
    }, {
        type    : 'Button',
        config  : {
            element     : '#viz_export',
            dont_wake   : function () {
                return ! uijet.Resource('ToolState').has('id');
            }
        }
    }, {
        type    : 'Button',
        config  : {
            element     : '#viz_publish',
            dont_wake   : function () {
                return ! uijet.Resource('ToolState').has('id');
            }
        }
    }, {
        factory : 'ChartMenuButton',
        config  : {
            element     : '#viz_delete',
            dont_wake   : function () {
                var state = uijet.Resource('ToolState');
                if ( uijet.Resource('LoggedinUser').get('id') === state.get('author') ) {
                    return ! state.has('id');
                }

                return true;
            },
            app_events  : {
                state_cleared       : enableMenuButton,
                state_delete_failed : enableMenuButton
            }
        }
    }, {
        factory : 'ChartMenuButton',
        config  : {
            element     : '#viz_duplicate',
            app_events  : {
                state_saved         : enableMenuButton,
                state_save_failed   : enableMenuButton
            }
        }
    }, {    
        factory : 'ChartMenuButton',
        config  : {
            element     : '#viz_save',
            dont_wake   : false,
            signals : {
                pre_click   : function () {
                    if ( ! uijet.Resource('LoggedinUser').has('id') ) {
                        uijet.publish('login');
                        return false;
                    }
                    else {
                        this.disable().spin();
                    }
                }
            },
            app_events  : {
                state_saved : enableMenuButton
            }
        }
    }];
});
