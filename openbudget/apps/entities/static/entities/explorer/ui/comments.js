define([
    'uijet_dir/uijet',
    'api',
    'resources'
], function (uijet, api) {

    var getUserAvatar = function () {
            return function (text, render) {
                return render(text).replace(/s=\d+/, 's=25');
            };
        },
        new_comment_data = {
            discussion  : {
                uuid            : '',
                comment         : '',
                created_on      : '',
                user            : window.LOGGEDIN_USER,
                get_user_avatar : getUserAvatar
            }
        };

    uijet.Resource('NewComment', uijet.Model());

    return [{
        type    : 'Button',
        config  : {
            element     : '#items_comments_close',
            dont_wake   : true,
            signals     : {
                pre_click   : 'sleep'
            },
            app_events  : {
                'open_comments' : 'wake'
            }
        }
    }, {
        type    : 'Pane',
        config  : {
            element     : '#items_comments_container',
//            mixins      : ['Scrolled'],
//            adapters    : ['jqWheelScroll'],
            resource    : 'NewComment',
            dont_wake   : true,
            signals     : {
                post_init   : function () {
                    this.$description = this.$element.find('#item_description')
                }
            },
            data_events : {
                'change:comment': function (model, comment) {
                    api.itemComments(this.resource.get('item_pk'), {
                        type: 'POST',
                        data: {
                            comment : comment
                        }
                    });
                }
            },
            app_events  : {
                'open_comments'                 : function ($selected) {
                    var item = uijet.Resource('LatestSheet').get(+$selected.attr('data-item')),
                        discussion = item.get('discussion'),
                        description = item.get('description');
                    this.$element[0].style.setProperty('padding-top', (uijet.utils.getOffsetOf($selected[0], uijet.$element[0]).y + 22) + 'px');
                    if ( description ) {
                        this.$element.removeClass('no_description');
                        this.$description.text(description);
                    }
                    else {
                        this.$element.addClass('no_description');
                    }

                    this.resource.set('item_pk', $selected.attr('data-item'));

                    this.wake({
                        discussion  : discussion
                    });
                },
                'items_comments_close.clicked'  : 'sleep'
            }
        }
    }, {
        type    : 'List',
        config  : {
            element     : '#item_comments_list',
            mixins      : ['Templated'],
            dont_fetch  : true,
            signals     : {
                
            },
            app_events  : {
                'add_comment.clicked'       : function () {
                    this.$new_comment = this.$element.append(this.template(new_comment_data))
                        .children().last();
                    uijet._translate(this.$new_comment[0]);
                },
                'new_comment_cancel.clicked': function () {
                    if ( this.$new_comment ) {
                        this.$new_comment.remove();
                        delete this.$new_comment;
                    }
                }
            }
        }
    }, {
        type    : 'Button',
        config  : {
            element     : '#add_comment',
            signals     : {
                pre_click   : 'sleep'
            },
            app_events  : {
                'new_comment_ok.clicked'    : 'wake',
                'new_comment_cancel.clicked': 'wake'
            }
        }
    }, {
        type    : 'Pane',
        config  : {
            element     : '#new_comment',
            resource    : 'NewComment',
            dont_wake   : true,
            signals     : {
                post_init   : function () {
                    this.$textarea = this.$element.find('textarea');
                    this.$textarea.on('keyup', function (e) {
                        if ( this.scrollHeight > this.clientHeight ) {
                            this.style.height = this.scrollHeight + 'px';
                        }
                    });
                },
                pre_wake    : function () {
                    this.$element.removeClass('hide');
                },
                post_appear : function () {
                    this.$textarea.focus();
                },
                pre_sleep   : function () {
                    var textarea = this.$textarea[0];
                    textarea.value = '';
                    textarea.style.removeProperty('height');
                    this.$element.addClass('hide');
                }
            },
            data_events : {},
            app_events  : {
                'add_comment.clicked'           : 'wake',
                'new_comment_ok.clicked'        : function () {
                    this.resource.set('comment', this.$textarea.val());
                },
                'new_comment_cancel.clicked'    : 'sleep',
                'open_comments'                 : 'sleep',
                'items_comments_close.clicked'  : 'sleep'
            }
        }
    }, {
        type    : 'Button',
        config  : {
            element : '#new_comment_ok'
        }
    }, {
        type    : 'Button',
        config  : {
            element : '#new_comment_cancel'
        }
    }];
});
