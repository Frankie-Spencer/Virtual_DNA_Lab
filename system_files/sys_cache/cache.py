
write_b_source = 'wbs'
run_b_source, run_b_des = 'rbs', 'rbd'
visual_b_source, visual_b_des = 'vbs', 'vbd'
import_seq = 'isf'
save_species_file = 'spf'
run_advanced_browse = 'rab'
web_browser_loc = 'wbl'

what_loc = {write_b_source: 'system_files/sys_cache/_write_source_loc.cache',
            run_b_source: 'system_files/sys_cache/_run_source_loc.cache',
            run_b_des: 'system_files/sys_cache/_run_des_loc.cache',
            import_seq: 'system_files/sys_cache/_write_import_loc.cache',
            visual_b_source: 'system_files/sys_cache/_visual_source_loc.cache',
            visual_b_des: 'system_files/sys_cache/_visual_des_loc.cache',
            save_species_file: 'system_files/sys_cache/_save_species_file_loc.cache',
            run_advanced_browse: 'system_files/sys_cache/_run_advanced_browse_loc.cache',
            web_browser_loc: 'system_files/sys_cache/_browser_loc.cache'}


def read_s_loc(what):

    with open(what_loc[what], 'r') as cf:
        li = cf.readline()
        cf.close()
        return li


def write_s_loc(what, l):

    with open(what_loc[what], 'w') as cf:
        cf.writelines(l)
        cf.close()


def read_d_loc(what):

    with open(what_loc[what], 'r') as cf:
        li = cf.readline()
        cf.close()
        return li


def write_d_loc(what, l):
    with open(what_loc[what], 'w') as cf:
        cf.writelines(l)
        cf.close()
