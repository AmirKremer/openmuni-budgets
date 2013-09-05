define([
    'uijet_dir/uijet',
    'modules/data/backbone',
    'underscore',
    'api',
    'modules/promises/q',
    'backbone-fetch-cache'
], function (uijet, Backbone, _, api) {

    uijet.use({
        prop: function (property) {
            return function (obj) {
                return obj[property];
            };
        }
    }, uijet.utils);

    var reverseSorting = function (field) {
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
                var collection = a.collection,
                    a_attrs = a.attributes,
                    b_attrs = b.attributes,
                    a_ancestors = a_attrs.ancestors,
                    b_ancestors = b_attrs.ancestors,
                    n = 0, m = 0, 
                    a_top = a, b_top = b,
                    go_deeper = true,
                    a_code, b_code;
    
                do {
                    if ( a_ancestors[n] ) {
                        a_top = collection.get(a_ancestors[n]);
                        n += 1;
                    }
                    else {
                        go_deeper = false;
                        a_top = a;
                    }
                    if ( b_ancestors[m] ) {
                        b_top = collection.get(b_ancestors[m]);
                        m += 1;
                    }
                    else {
                        go_deeper = false;
                        b_top = b;
                    }
                }
                while ( go_deeper && a_top.id === b_top.id );
    
                a_code = a_top.get('code');
                b_code = b_top.get('code');
    
                // if `a` and `b` are not in same level
                return a_code == b_code ?
                    // check if `a` is higher in the hierarchy, otherwise `b` is
                    a_top === a ?
                        a_is_smaller : a_is_bigger :
                    // if they are in same level order by code
                    a_code < b_code ? a_is_smaller : a_is_bigger;
            };
        },
        /*
         * User (Account) Model
         */
        User = uijet.Model({
            idAttribute : 'uuid',
            name        : function () {
                var first = this.get('first_name'),
                    last = this.get('last_name');
                if ( first || last ) {
                    return first + ' ' + last;
                }
                else {
                    return gettext('Guest:');
                }
            },
            avatar      : function () {
                var avatar = this.get('avatar');
                return avatar ? avatar.replace(/s=\d+[^&]/i, 's=90') : window.DEFAULT_AVATAR;
            }
        }),
        /*
         * Muni (Entity) Model
         */
        Muni = uijet.Model({
            idAttribute : 'id'
        }),
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
            idAttribute : 'id',
            branchName  : function (from_id) {
                var ancestors = this.attributes.ancestors,
                    index = from_id ? ancestors.indexOf(from_id) : null,
                    result = [],
                    ancestors_len = ancestors.length;

                if ( index === null ) {
                    index = 0;
                }
                else if ( ~ index ) {
                    index += 1;
                }

                while ( ancestors_len > index ) {
                    ancestors_len -= 1;
                    result.unshift(this.collection.get(ancestors[ancestors_len]).get('name'));
                }

                return result;
            }
        }),
        /*
         * TemplateNodes Collection
         */
        Nodes = uijet.Collection({
            model           : Node,
            url             : function () {
                return api.getRoute('templateNodes');
            },
            comparator      : function (a, b) {
                var a_attrs = a.attributes,
                    b_attrs = b.attributes,
                    diff = a_attrs.level - b_attrs.level;
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
             * Setting `ancestors` array of `id`s, `leaf_node` boolean flag and
             * `level` - a Number representing the level of the node in the tree.
             * 
             * @param {Object|Array} response
             * @returns {Object|Array} response
             */
            parse           : function (response) {
                var results = response.results,
                    last = results.length - 1,
                    paths_lookup = {},
                    parent_ids = {},
                    node, n, route, path, ancestor;
                /* 
                 * first loop
                 *
                 * init `ancestor` to `[]` 
                 * create `paths_lookup` to look up nodes by `path`
                 * create `parent_ids` to look up child nodes by `parent` (by id later)
                 * set `level` by splitting `path` and checking its `length`
                 * set `parent` to the parent's id
                 */
                for ( n = last; node = results[n]; n-- ) {
                    node.ancestors = [];
                    node.level = node.path.split('|').length - 1;
                    paths_lookup[node.path] = node;
                    if ( node.parent ) {
                        node.parent = node.parent.id || node.parent;
                        if ( ! parent_ids[node.parent] ) {
                            parent_ids[node.parent] = [];
                        }
                        parent_ids[node.parent].push(node.id);
                    }
                    node.direction = gettext(node.direction);
                }
                /*
                 * second loop
                 * 
                 * set `children` to the array in `parent_ids` using `id`
                 * set `leaf_node` to `true` if `id` is not in `parent_ids`
                 * fill `ancestors` array by ancestor `id`s ordered by `level` as index
                 */
                for ( n = last; node = results[n]; n-- ) {
                    if ( parent_ids[node.id] ) {
                        node.children = parent_ids[node.id];
                    }
                    else {
                        node.leaf_node = true;
                    }
                    route = node.path.split('|').slice(1);
                    while ( route.length ) {
                        path = route.join('|');
                        if ( path in paths_lookup ) {
                            ancestor = paths_lookup[path];
                            node.ancestors[ancestor.level] = ancestor.id;
                        }
                        route.shift();
                    }
                }
                paths_lookup = null;
                parent_ids = null;

                return results;
            },
            roots           : function () {
                return this.byParent(null);
            },
            byParent        : function (parent_id) {
                return this.where({
                    parent  : parent_id
                });
            },
            byAncestor      : function (ancestor_id) {
                if ( ancestor_id ) {
                    return this.filter(function (node) {
                        return ~ node.attributes.ancestors.indexOf(ancestor_id);
                    });
                }
                else {
                    return this.models;
                }
            },
            branch          : function (node_id) {
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
        Context = uijet.Model({
            parse   : function (response) {
                response.data = JSON.parse(response.data);
                return response;
            }
        }),
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
        State = uijet.Model({
            idAttribute : 'uuid',
            urlRoot     : function () {
                return api.getRoute('projectStates');
            },
            url         : function () {
                return this.urlRoot() + (this.id ? this.id + '/' : '');
            },
            parse       : function (response) {
                var user = new User(response.author);
                response.author_model = user;
                response.author = user.id;
                return response;
            }
        });

    return {
        User    : User,
        Muni    : Muni,
        Munis   : Munis,
        Node    : Node,
        Nodes   : Nodes,
        State   : State,
        Context : Context,
        Contexts: Contexts,
        utils   : {
            reverseSorting      : reverseSorting,
            nestingSort         : nestingSortFactory(false),
            reverseNestingSort  : nestingSortFactory(true)
        },
        '_'     : _
    };
});
