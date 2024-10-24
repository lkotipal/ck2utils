
#include "bmp_format.h"
#include "error.h"
#include "default_map.h"
#include "province_map.h"
#include "terrain.h"
#include "pdx.h"

#include <boost/filesystem.hpp>

#include <cstdio>
#include <cerrno>
#include <cstring>
#include <cassert>
#include <vector>
#include <algorithm>


using namespace boost::filesystem;


const path VROOT_PATH("D:/SteamLibrary/steamapps/common/Crusader Kings II");
//const path ROOT_PATH(VROOT_PATH);
const path ROOT_PATH("D:/g/SWMH-BETA/SWMH");


struct province {
    uint id;
    std::string county; // empty when N/A (sea zones, wasteland, etc.)
    int max_settlements; // -1 for undefined
    int terrain_id; // before automatic terrain assignment, -1 for implicit

    // array of terrain-type pixel counts, indexed by terrain type ID
    uint terrain_px_array[NUM_TERRAIN];

    province(uint _id)
    : id(_id), max_settlements(-1), terrain_id(-1) {
        for (auto&& c : terrain_px_array) c = 0;
    }
};


void read_province_history(const default_map&, const definitions_table&, std::vector<province>&);
int terrain_name_to_id(const char*);


int main(int argc, char** argv) {

    try {
        default_map dm(ROOT_PATH);
        definitions_table def_tbl(dm);

        std::vector<province> pr_tbl;
        pr_tbl.reserve( def_tbl.row_vec.size() );
        read_province_history(dm, def_tbl, pr_tbl);

        char buf[64];

        while (fgets(&buf[0], sizeof(buf), stdin) != nullptr) {
            char* s = strchr(buf, '=');
            assert(s);
            *s = '\0';
            const char* terrain = s+1;
            s = strchr(terrain, '\n');
            assert(s);
            *s = '\0';

            int id = atoi(buf);
            assert(id > 0);
            int terrain_id = terrain_name_to_id(terrain);

            if (terrain_id < 0)
                throw va_error("unrecognized terrain type from standard input: '%s'", terrain);

            pr_tbl[id-1].terrain_id = terrain_id;
        }

        province_map pm(dm, def_tbl);

        const char* path = dm.terrain_path().c_str();
        FILE* f;

        if ( (f = fopen(path, "rb")) == nullptr )
            throw va_error("could not open file: %s: %s", strerror(errno), path);

        bmp_file_header bf_hdr;
        errno = 0;

        if ( fread(&bf_hdr, sizeof(bf_hdr), 1, f) < 1 ) {
            if (errno)
                throw va_error("failed to read bitmap header: %s: %s", strerror(errno), path);
            else
                throw va_error("unexpected EOF while reading bitmap header: %s", path);
        }

        /* format stuff */
        assert(bf_hdr.magic == BMP_MAGIC);
        assert(bf_hdr.n_header_size >= 40); // at least a BITMAPINFOHEADER (v3)
        assert(bf_hdr.n_width > 0 && bf_hdr.n_width % 4 == 0);
        assert(bf_hdr.n_height > 0);
        assert(bf_hdr.n_planes == 1);
        assert(bf_hdr.n_bpp == 8);
        assert(bf_hdr.compression_type == 0);

        /* higher-level asserts */
        assert( (unsigned)bf_hdr.n_width == pm.width());
        assert( (unsigned)bf_hdr.n_height == pm.height());

        /* we don't even need to read the color table, as the indices are all we need for our purposes,
         * but it's nice to see that the correct colors are indeed in the table, so we'll print them
         * for the user */

        uint palette_offset = bf_hdr.n_header_size + sizeof(bf_hdr) - 40;

        /* the "minus one" below is because, apparently, the final terrain texture type (forest)
         * does not actually get any representation in the color table. this is vaguely correlated
         * with the inflection of some old Swedish comment next to it in terrain.txt */
        const uint n_colors = NUM_TERRAIN_COLORS-1;

        assert( !( bf_hdr.n_colors && bf_hdr.n_colors < n_colors ) ); // we expect at least enough colors for our terrain

        if ( fseek(f, palette_offset, SEEK_SET) != 0 )
            throw va_error("failed to seek to color table (offset=%u): %s: %s",
                           palette_offset,
                           strerror(errno),
                           path);

        fprintf(stderr, "relevant color table entries in terrain bitmap:\n");

        for (uint i = 0; i < n_colors; ++i) {
            uint8_t bgra[4];

            if ( fread(&bgra[0], sizeof(bgra), 1, f) < 1 ) {
                if (errno)
                    throw va_error("failed to read color index %u from color table: %s: %s",
                                   i, strerror(errno), path);
                else
                    throw va_error("unexpected EOF while reading color index %u from color table: %s",
                                   i, path);
            }

            const char* name = TERRAIN[ TERRAIN_COLOR_TO_ID[i] ].name.c_str();
            fprintf(stderr, "%2u: RGB(%3hhu, %3hhu, %3hhu): %s\n", i, bgra[2], bgra[1], bgra[0], name);
        }

        if ( fseek(f, bf_hdr.n_bitmap_offset, SEEK_SET) != 0 )
            throw va_error("failed to seek to raw bitmap data (offset=%u): %s: %s",
                           bf_hdr.n_bitmap_offset,
                           strerror(errno),
                           path);

        const int width = pm.width();
        const int height = pm.height();
        uint8_t row[width];
        const uint16_t* pm_map = pm.map();

        for (int y = height-1; y >= 0; --y) {

            if ( fread(row, 1, width, f) < (unsigned)width ) {
                if (errno)
                    throw va_error("failed to read pixel array row (y=%d): %s: %s", y, strerror(errno), path);
                else
                    throw va_error("unexpected EOF while reading row in pixel array (y=%d): %s", y, path);
            }

            const uint16_t* pm_row = &pm_map[y * width];

            for (int x = 0; x < width; ++x) {
                if (pm_row[x] == province_map::TYPE_OCEAN || pm_row[x] == province_map::TYPE_IMPASSABLE)
                    continue; // pixel belongs to no province

                province& pr = pr_tbl[ pm_row[x] - 1 ];

                if (pr.terrain_id >= 0)
                    continue; // terrain has already been assigned

                if (row[x] >= n_colors)
                    throw va_error("unexpected color index %hhu in terrain bitmap at (x,y)=(%d, %d): %s",
                                   row[x], x, y, path);

                ++pr.terrain_px_array[ TERRAIN_COLOR_TO_ID[ row[x] ] ];
            }
        }

        for (auto&& pr : pr_tbl) {
            if (pr.terrain_id < 0) // not already assigned terrain
                pr.terrain_id = std::max_element(pr.terrain_px_array,
                                                 pr.terrain_px_array + NUM_TERRAIN) - pr.terrain_px_array;

            printf("%u = {\n", pr.id);

            if (!pr.county.empty())
                printf("   title=%s\n", pr.county.c_str());

            printf("   max_settlements=%d\n", (pr.max_settlements < 0) ? 7 : pr.max_settlements);
            printf("   terrain=%s\n}\n", TERRAIN[ pr.terrain_id ].name.c_str());
        }

        fclose(f);
    }
    catch (std::exception& e) {
        fprintf(stderr, "fatal: %s\n", e.what());
        return 1;
    }

    return 0;
}


void read_province_history(const default_map& dm,
                           const definitions_table& def_tbl,
                           std::vector<province>& pr_tbl) {

    path hist_root = ROOT_PATH / "history/provinces";
    path hist_vroot = VROOT_PATH / "history/provinces";

    uint id = 0;
    char filename[256];

    for (auto&& def : def_tbl.row_vec) {
        ++id;

        pr_tbl.emplace_back(id);
        province& pr = pr_tbl.back();

        if (def.name.empty()) // wasteland | external
            continue;
        if (dm.id_is_seazone(id)) {
            pr.terrain_id = TERRAIN_ID_WATER;
            continue;
        }

        sprintf(filename, "%u - %s.txt", id, def.name.c_str());

        path hist_file = hist_root / filename;

        if (!exists(hist_file)) {
            path hist_vfile = hist_vroot / filename;

            if (!exists(hist_vfile))
                throw va_error("could not find province history file implied by definitions table: %s", filename);
            else
                hist_file = hist_vfile;
        }

        const char* county = nullptr;
        const char* terrain = nullptr;
        int max_settlements = -1;


        pdx::plexer lex(hist_file.c_str());
        pdx::block doc(lex, true);

        for (auto&& s : doc.stmt_list) {
            if (s.key_eq("title"))
                county = s.val.as_title();
            else if (s.key_eq("terrain"))
                terrain = s.val.as_c_str();
            else if (s.key_eq("max_settlements"))
                max_settlements = s.val.as_integer();
        }

        assert( !( county && (max_settlements < 0 || max_settlements > 7) ) );

        if (county) {
            assert( pdx::title_tier(county) == pdx::TIER_COUNT );

            pr.county = county;
            pr.max_settlements = max_settlements;
        }

        if (terrain) {
            pr.terrain_id = terrain_name_to_id(terrain);

            if (pr.terrain_id < 0)
                throw va_error("unknown terrain type '%s' in province history file: %s",
                               terrain, hist_file.c_str());
        }
    }
}


int terrain_name_to_id(const char* name) {
    for (int i = 0; i < NUM_TERRAIN; ++i)
        if (TERRAIN[i].name == name)
            return i;

    return -1;
}
