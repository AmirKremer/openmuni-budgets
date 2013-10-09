define([
    'embed_widgets/TimelineChartEmbed',
    'controllers/TimelineChart'
], function () {

    return [{
        type    : 'TimelineChartEmbed',
        config  : {
            element : '#chart',
            adapters: ['TimelineChart'],
            resource: 'TimeSeries',
            chart   : {
                padding         : 20,
                axes_y_orient   : 'right'
            },
            signals : {
                pre_render  : '_draw'
            }
        }
    }];

});
