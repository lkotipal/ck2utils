
#include "default_map.h"

#include "pdx.h"
#include "error.h"

#include <cassert>


default_map::default_map(const std::string& root_path)
: _max_province_id(0) {

    using namespace pdx;

    const std::string path = root_path + "/map/default.map";
    plexer lex(path.c_str());
    block doc(lex, true);

    for (auto&& s : doc.stmt_list) {
        if (s.key_eq("max_provinces")) {
            assert( s.val.type == obj::INT && s.val.data.i > 1 );
            _max_province_id = s.val.data.i - 1;
        }
        else if (s.key_eq("definitions")) {
            assert(s.val.type == obj::STR);
            _definitions_path = root_path + "/map/" + s.val.data.s;
        }
        else if (s.key_eq("provinces")) {
            assert(s.val.type == obj::STR);
            _provinces_path = root_path + "/map/" + s.val.data.s;
        }
        else if (s.key_eq("sea_zones")) {
            assert(s.val.type == obj::LIST);

            auto&& obj_list = s.val.data.p_list->obj_list;
            assert( obj_list.size() == 2 );

            for (auto&& o : obj_list)
                assert( o.type == obj::INT && o.data.i > 0 );

            _seazone_vec.emplace_back( uint(obj_list[0].data.i), uint(obj_list[1].data.i) );
        }
        else if (s.key_eq("major_rivers")) {
            assert(s.val.type == obj::LIST);
            auto&& obj_list = s.val.data.p_list->obj_list;

            for (auto&& o : obj_list) {
                assert( o.type == obj::INT && o.data.i > 0 );
                _major_river_set.insert(o.data.i);
            }
        }
    }

    assert( max_province_id() > 0 );
}


bool default_map::id_is_seazone(uint prov_id) const {
    if (!id_is_valid(prov_id))
        return false;

    for (auto&& sea_range : _seazone_vec)
        if (prov_id >= sea_range.first && prov_id <= sea_range.second)
            return true;

    return false;
}