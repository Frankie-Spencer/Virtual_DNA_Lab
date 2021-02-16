import sys
from PySide2.QtCore import (QCoreApplication, QMetaObject, QObject, QPoint,
    QRect, QSize, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
    QFontDatabase, QIcon, QLinearGradient, QPalette, QPainter, QPixmap,
    QRadialGradient)
from PySide2.QtWidgets import *
from sys_cache.cache import read_s_loc, write_s_loc, read_d_loc, write_d_loc
import os, time, threading, webbrowser, shutil
from dump_to_species_converter_v26 import dump_to_species
import browse_and_parse_v03
from extract_ssdna_from_data_v02 import extract_ssdna
from make_rnf_v07 import make_rnf_file
from math import ceil


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        global write_edited_amount_g, write_edited_seq_g, advanced_criteria, advanced_criteria_text, ssdna_comp_list, \
            imp_seq_temp, type_dic_ssdna_comp, vis_adv_ranges_g, \
            run_kt_list_g, run_temper_data_g, run_time_data_g, run_annealing_g, run_kt_g, \
            write_kt_list_g, write_kt_status_g, \
            validate_float, validated_float_g, validated_int_g, \
            save_species_file, run_advanced_browse, advanced_bngl_path, run_set_source

        run_kt_list_g, run_temper_data_g, run_time_data_g = {}, ['', '', ''], ['', '', '']
        run_kt_g, run_annealing_g = False, False

        write_kt_list_g, write_kt_status_g = {}, False

        validate_float, validated_float_g, validate_int, validated_int_g = 'vaf', '', 'vag', ''

        type_dic_ssdna_comp = {1: 'ssDNA(s)    ', 2: 'complex(es) ', 'spaces': int}

        write_edited_amount_g, write_edited_seq_g = '', ''
        vis_adv_ranges_g = ''
        advanced_criteria, advanced_criteria_text = [], []
        imp_seq_temp = []
        ssdna_comp_list = []

        begin_species, end_species, ti = 'begin species', 'end species', [0]
        begin_parameters, end_parameters = 'begin parameters', 'end parameters'
        write_b_source = 'wbs'
        run_b_source, run_b_des = 'rbs', 'rbd'
        save_species_file = 'spf'
        visual_b_source, visual_b_des = 'vbs', 'vbd'
        write_tab, run_tab, visual_tab = 'write', 'run', 'vis'
        write_the_seq, write_n_seq = 'wts', 'rns'
        run_start_time, run_n_dumps, run_sim_end, run_run = 'rst', 'rnd', 'rse', 'rr'
        import_seq = 'isf'
        species_type, dump_type, bngl_type = 'species', '0', 'bngl'
        write_edit_seq, write_edit_amount = 'res', 'wea'
        vis_adv_ranges = 'var'
        info_request = 'inr'
        run_advanced_browse = 'rab'
        web_browser_loc = 'wbl'
        species_file_default_path = os.path.realpath(__file__).replace('\\', '/').rsplit('/', 2)[0] + \
                                    '/saved_test_tube_files/my_test_tube_file.species'
        species_file_system_path = os.path.realpath(__file__).replace('\\', '/').rsplit('/', 1)[0] + \
                                    '/reference_files/current_test_tube_file.species'

        bngl_file_system_path = os.path.realpath(__file__).replace('\\', '/').rsplit('/', 1)[0] + \
                                    '/reference_files/reference_file.bngl'

        advanced_bngl_path = ''
        run_set_source = ''

        def run_in_thread(fn):
            def run(*k, **kw):
                t = threading.Thread(target=fn, args=k, kwargs=kw)
                t.start()
                return t

            return run

        def get_user_consent(consent_for, s):
            consent_check = QMessageBox()

            con_dic = {'write_reset': 'Resetting will remove all created sequences. '
                                      'This action cannot be undone!\n' +
                                      '\n'
                                      'Click "Yes" to reset for a fresh start\n'
                                      'Click "No" to return back',

                       'delete_folder': 'Are you sure you want to permanently delete this folder?\n' +
                                        '\n' +
                                        s[0],

                       'delete_seq_comp': 'Are you sure you want to permanently delete this ' + s[1] + '?\n' +
                                          '\n' +
                                          s[0],

                       'simulate_line': 'Unable to process the given input file, because it contains the '
                                        'following syntax.\n' +
                                        '\n' +
                                        'line ' + s[1] + ':\n' +
                                        s[0] + '\n' +
                                        'Click "Yes" if you consent the program to comment out this line\n' +
                                        'Click "No" if you wish to do it manually',

                       'web_browser_get': 'To visualize complexes the program requires Chrome browser.\n'
                                          'This program needs to know where chrome.exe installed at first\n' +
                                          '\n' +
                                          'Click "Yes" to navigate to chrome.exe\n'
                                          'Click "No" if you do not need visualization'
                       }

            if consent_for == 'write_reset' or consent_for == 'delete_folder' or consent_for == 'delete_seq_comp':
                consent_check.setWindowTitle('Warning!')
                consent_check.setText(con_dic[consent_for])
                consent_check.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                consent = consent_check.exec_()

                return consent

            elif consent_for == 'simulate_line':
                self.label_messages.setText('Input file validation error ✘')

                consent_check.setWindowTitle('BNGL file validation error')
                consent_check.setText(con_dic[consent_for])
                consent_check.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                consent = consent_check.exec_()

                return consent

            elif consent_for == 'web_browser_get':
                self.label_messages.setText('Chrome browser not found ✘')

                consent_check.setWindowTitle('Provide Chrome browser link')
                consent_check.setText(con_dic[consent_for])
                consent_check.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                consent = consent_check.exec_()

                return consent

        def update_history():
            sele_folder_dir = self.lineEdit_visual_browse_des.text()

            if os.path.isdir(sele_folder_dir):
                self.listWidget_visual_history_list.clear()
                self.pushButton_visual_view_comp.setDisabled(True)
                self.pushButton_visual_view_bngl.setDisabled(True)
                self.pushButton_visual_view_source.setDisabled(True)
                self.pushButton_visual_delete.setDisabled(True)
                sele_folder = list(next(os.walk(sele_folder_dir))[:-1])

                c_time_dic_all = {}
                for dir in sele_folder[1]:
                    c_time_dic = {dir: os.stat(sele_folder[0] + '/' + dir).st_ctime}
                    c_time_dic_all.update(c_time_dic)

                sorted_all = dict(sorted(c_time_dic_all.items(), key=lambda kv: kv[1], reverse=True))

                for x in sorted_all:
                    if x != '':
                        self.listWidget_visual_history_list.insertItem(len(sorted_all), '✅  ' + str(x))
            else:
                self.listWidget_visual_history_list.clear()
                self.pushButton_visual_view_comp.setDisabled(True)
                self.pushButton_visual_view_bngl.setDisabled(True)
                self.pushButton_visual_view_source.setDisabled(True)
                self.pushButton_visual_delete.setDisabled(True)

        def set_species_save_dir(a):
            cus_checked = self.checkBox_custom_file_name.isChecked()

            if cus_checked:
                self.lineEdit_custom_file_name.setText(species_file_default_path)

            else:
                self.lineEdit_custom_file_name.setText('')

        def validate_path_link(link):
            chars = ['#']
            chars_in_link = []

            for c in link:
                if c in chars:
                    chars_in_link.append(c)
            if chars_in_link == []:
                return [True, '']

            elif chars_in_link != []:
                chars_list = '   ' + '  '.join(chars_in_link) + '   '
                return [False, chars_list]

        def input_file_validations(file_path, validate_call_from):

            global run_kt_list_g, write_kt_status_g, write_kt_list_g, run_kt_status_g

            source_file_dic = {run_b_source: self.lineEdit_run_browse_source.text(),
                               import_seq: file_path,
                               run_run: file_path,
                               visual_b_source: self.lineEdit_visual_browse_source.text()}

            source_file_req = source_file_dic[validate_call_from]

            def validate_file(f_path, v_call_from):

                file_exists = os.path.isfile(f_path)

                if file_exists:
                    if v_call_from == write_b_source:
                        check_b_n_e = []
                        with open(f_path, 'r') as f:
                            a = f.readlines()
                            for i in a:
                                check_syn = i.rstrip('\n').rstrip()
                                if check_syn == begin_species:
                                    check_b_n_e.append(begin_species)

                                elif check_syn == end_species:
                                    check_b_n_e.append(end_species)

                        if begin_species in check_b_n_e and end_species in check_b_n_e:
                            return 'ready'
                        else:
                            none = check_b_n_e[0] if check_b_n_e != [] else 'none'
                            return none

                    elif v_call_from == run_b_source or v_call_from == run_run:
                        def re_write_input_file(c):

                            data = []

                            with open(c, 'r') as f:
                                a = f.readlines()
                                for i in a:
                                    if not i.startswith('simulate'):
                                        data.append(i)

                                    elif i.startswith('simulate'):
                                        new_line = '# ' + i
                                        data.append(new_line)
                            f.close()

                            with open(c, 'w') as f:
                                for item in data:
                                    f.write("%s" % item)
                            f.close()
                            return True

                        check_simulate = []
                        with open(f_path, 'r') as f:
                            a = f.readlines()
                            line_n = 0
                            for i in a:
                                line_n += 1
                                if i.startswith('simulate'):
                                    check_simulate.append(i)
                                    check_simulate.append(line_n)
                        f.close()

                        if check_simulate == []:
                            return True

                        elif check_simulate != []:
                            consent = get_user_consent('simulate_line', [check_simulate[0], str(check_simulate[1])])
                            if consent == 16384:
                                re_write_input_file(f_path)
                                return True
                            elif consent == 65536:
                                return False

                    elif v_call_from == import_seq or v_call_from == visual_b_source:
                        check_type = file_path.rsplit('/', 1)[1].rsplit('.', 1)[1]
                        imported_seqs = []
                        global run_status
                        run_status = None

                        @run_in_thread
                        def import_sep_thread(file_type):
                            global imp_seq_temp, run_status

                            def fr_dump():
                                dump_convert = dump_to_species(f_path, '', '', 'read_dump')
                                if dump_convert != False:
                                    get_ssdna = extract_ssdna('', 'read_species', dump_convert)
                                    return get_ssdna
                                else:
                                    return False

                            r_type_dic = {'0': fr_dump(),
                                          'species': extract_ssdna('', 'read_species', imported_seqs)}

                            import_run = list(r_type_dic[file_type])

                            if import_run != False:
                                imp_seq_temp = import_run
                                run_status = True
                            else:
                                run_status = False

                        with open(f_path, 'r') as f:
                            if check_type == species_type:
                                a = f.readlines()
                                for i in a:
                                    if i.startswith('N('):
                                        seq = str(i.rstrip('\n').rstrip()).rsplit('  ', 1)
                                        if seq[0].startswith('N(') and seq[1].isdigit():
                                            imported_seqs.append(seq[0] + '  ' + seq[1])
                                        else:
                                            return False

                                if v_call_from == import_seq:
                                    import_sep_thread('species')
                                    while run_status == None:
                                        time.sleep(0.1)

                                    if run_status == True:
                                        return True
                                    else:
                                        return False

                                elif v_call_from == visual_b_source:
                                    return [True, species_type]

                            elif check_type == dump_type:
                                if v_call_from == visual_b_source:
                                    return [True, dump_type]

                                elif v_call_from == import_seq:
                                    import_sep_thread('0')
                                    while run_status == None:
                                        time.sleep(0.1)

                                    if run_status == True:
                                        return True
                                    else:
                                        return False
                                else:
                                    return False

                else:
                    return 'file_not_exists'

            validate_check = validate_file(file_path, validate_call_from)

            if validate_call_from == run_b_source or validate_call_from == run_run:

                if validate_check == True:
                    write_s_loc(run_b_source, file_path)
                    self.label_messages.setText('BNGL file selected ✔')

                    if validate_call_from == run_b_source:
                        run_kt_list_g = {}
                        run_kt_status_g = False
                        self.checkBox_run_advanced.setChecked(False)

                elif validate_check == False:
                    self.lineEdit_run_browse_source.setText('')
                    self.label_messages.setText('BNGL file not selected ✘')

                elif not os.path.isfile(file_path) and os.path.isfile(source_file_req):
                    if validate_file(source_file_req, validate_call_from):
                        write_s_loc(run_b_source, source_file_req)
                        self.label_messages.setText('New BNGL file not selected, returned to previous ✔')

                    else:
                        self.lineEdit_run_browse_source.setText('')
                        self.label_messages.setText('Please edit the BNGL file and try again!')

                elif not os.path.isfile(file_path) and not os.path.isfile(source_file_req):
                    self.lineEdit_run_browse_source.setText('')
                    self.label_messages.setText('Source file not selected ✘')

            elif validate_call_from == import_seq:
                if validate_check == True:
                    write_s_loc(import_seq, file_path)

                else:
                    self.label_messages.setText('Species/Dump file error, sequence(s) import unsuccessful ✘')

            elif validate_call_from == visual_b_source:
                dic_type = {'species': 'Species', '0': 'Dump'}
                if validate_check[0] == True:
                    write_s_loc(visual_b_source, file_path)
                    self.label_messages.setText(
                        'Selected source file recognized as "' + dic_type[validate_check[1]] + '" file ✔')

                elif not os.path.isfile(file_path) and os.path.isfile(source_file_req):
                    self.label_messages.setText('New source file not selected, returned to previous ✔')

                elif not os.path.isfile(file_path) and not os.path.isfile(source_file_req):
                    self.label_messages.setText('Source file not selected ✘, please try again!')

            return validate_check

        def validate_and_update_buttons(tab):

            if tab == write_tab:
                created_list = self.listWidget_write_list_created
                list_all = [created_list.item(index).text() for index in range(created_list.count())]
                cus_file_name = self.lineEdit_custom_file_name.text()
                cus_checked = len(cus_file_name) > 0 if self.checkBox_custom_file_name.isChecked() else True

                if cus_checked:
                    if len(list_all) > 0:
                        self.pushButton_save.setEnabled(True)

                    else:
                        self.pushButton_save.setDisabled(True)

                else:
                    self.pushButton_save.setDisabled(True)

                if len(list_all) > 0:
                    self.pushButton_write_reset_all.setEnabled(True)
                else:
                    self.pushButton_write_reset_all.setDisabled(True)

                if created_list.currentRow() == -1:
                    self.pushButton_write_delete.setDisabled(True)
                    self.pushButton_write_edit.setDisabled(True)
                else:
                    self.pushButton_write_delete.setEnabled(True)
                    self.pushButton_write_edit.setEnabled(True)

                if len(self.lineEdit_write_sequence.text()) >= 2 and len(
                        self.lineEdit_write_amount.text()) >= 1:
                    self.pushButton_write_add_sequence.setEnabled(True)
                else:
                    self.pushButton_write_add_sequence.setDisabled(True)

            elif tab == run_tab:
                start_time = self.lineEdit_run_start_time.text()
                end_time = self.lineEdit_run_sim_end.text()
                n_dumps = self.lineEdit_run_n_dumps.text()
                source_file_path = self.lineEdit_run_browse_source.text()
                des_dir_path = self.lineEdit_run_browse_des.text()

                st_time = str(start_time)[-1] if len(str(start_time)) > 0 else None
                ed_time = str(end_time)[-1] if len(str(end_time)) > 0 else None

                if os.path.isdir(des_dir_path):
                    validate_des_path_link = validate_path_link(des_dir_path)
                    if validate_des_path_link[0]:
                        if start_time != '' and end_time != '' and n_dumps != '':
                            if not st_time.endswith('.') and not ed_time.endswith('.'):
                                if float(start_time) != float(end_time):
                                    if float(start_time) < float(end_time):
                                        if float(end_time) > 0:
                                            if int(n_dumps) > 0:
                                                if os.path.isfile(source_file_path):
                                                    validate_s_path_link = validate_path_link(source_file_path)
                                                    if validate_s_path_link[0]:
                                                        if source_file_path.rsplit('/', 1)[1].rsplit('.', 1)[1] == species_type:
                                                            self.pushButton_run_run.setEnabled(True)
                                                            self.label_messages.setText('Program ready to run!')

                                                        else:
                                                            self.pushButton_run_run.setDisabled(True)
                                                            self.label_messages.setText(
                                                                'Input file error ✘, only ".species" files accepted!')

                                                    else:
                                                        self.label_messages.setText(
                                                            'Save directory cannot include special character(s) ' +
                                                            validate_s_path_link[1])

                                                else:
                                                    self.pushButton_run_run.setEnabled(True)
                                                    self.label_messages.setText('Program ready to run!')

                                            else:
                                                self.pushButton_run_run.setDisabled(True)
                                                self.label_messages.setText('"Number of dump files" '
                                                                            'must be a positive value ✘')

                                        else:
                                            self.pushButton_run_run.setDisabled(True)
                                            self.label_messages.setText('"End time" '
                                                                        'must be a positive value ✘')

                                    else:
                                        self.pushButton_run_run.setDisabled(True)
                                        self.label_messages.setText('"Start time" must be less than '
                                                                    '"End time" ✘')

                                else:
                                    self.pushButton_run_run.setDisabled(True)
                                    self.label_messages.setText('"Start time" and "End time" '
                                                                'cannot be same ✘')

                            else:
                                self.pushButton_run_run.setDisabled(True)
                                self.label_messages.setText('Error found on some fields, please check ✘')

                        else:
                            self.pushButton_run_run.setDisabled(True)
                            self.label_messages.setText('Any of the below fields cannot be empty ✘')

                    else:
                        self.pushButton_run_run.setDisabled(True)

                else:
                    self.pushButton_run_run.setDisabled(True)
                    self.label_messages.setText('Save simulation outputs directory not selected ✘')

            elif tab == visual_tab:
                created_list = self.listWidget_visual_history_list
                source_file_path = self.lineEdit_visual_browse_source.text()
                des_dir_path = self.lineEdit_visual_browse_des.text()

                accepted_types = [dump_type, species_type]

                if created_list.currentRow() == -1:
                    self.pushButton_visual_view_comp.setDisabled(True)
                    self.pushButton_visual_view_bngl.setDisabled(True)
                    self.pushButton_visual_delete.setDisabled(True)
                else:
                    if os.path.isdir(des_dir_path):
                        history_list = self.listWidget_visual_history_list
                        list_all = [history_list.item(index).text() for index in range(history_list.count())]
                        selection = list_all[history_list.currentRow()][3:]
                        selection_link = self.lineEdit_visual_browse_des.text() + '/' + selection

                        b_status = [False, False, False]
                        for file in os.listdir(selection_link):

                            if file.endswith('.html'):
                                b_status[0] = True

                            if file.endswith('.species') and '_result_species' in file:
                                b_status[1] = True

                            if file.endswith('.species') and '_source_species' in file:
                                b_status[2] = True

                        self.pushButton_visual_view_comp.setEnabled(b_status[0])
                        self.pushButton_visual_view_bngl.setEnabled(b_status[1])
                        self.pushButton_visual_view_source.setEnabled(b_status[2])

                        self.pushButton_visual_delete.setEnabled(True)

                if os.path.isfile(source_file_path):
                    validate_s_path_link = validate_path_link(source_file_path)
                    if validate_s_path_link[0]:
                        if source_file_path.rsplit('/', 1)[1].rsplit('.', 1)[1] in accepted_types:
                            if os.path.isdir(des_dir_path):
                                validate_des_path_link = validate_path_link(des_dir_path)
                                if validate_des_path_link[0]:
                                    self.pushButton_visual_visualize.setEnabled(True)
                                    self.label_messages.setText('Program ready to run!')
                                    return True

                                else:
                                    self.pushButton_visual_visualize.setDisabled(True)

                            else:
                                self.pushButton_visual_visualize.setDisabled(True)
                                self.label_messages.setText('Save visualization outputs directory not selected ✘')

                        else:
                            self.pushButton_visual_visualize.setDisabled(True)
                            self.label_messages.setText('Input file error ✘, only ".speceis" or ".0" files accepted!')

                    else:
                        self.pushButton_visual_visualize.setDisabled(True)

                else:
                    self.pushButton_visual_visualize.setDisabled(True)
                    self.label_messages.setText('Input dump/species file is not selected ✘')

        def on_edit_source_path(call_from, tab):
            source_file_dic = {run_b_source: self.lineEdit_run_browse_source.text(),
                               visual_b_source: self.lineEdit_visual_browse_source.text()}

            file_path = source_file_dic[call_from]

            validate_path_status = validate_path_link(file_path)

            if validate_path_status[0]:
                if os.path.isfile(file_path):
                    self.label_messages.setText('')
                    input_file_validations(file_path, call_from)
            else:
                self.label_messages.setText(
                    'Source path cannot include special character(s) ' + validate_path_status[1])

            validate_and_update_buttons(tab)

        def on_edit_des_dir(call_from, tab):
            des_dir_dic = {run_b_des: self.lineEdit_run_browse_des.text(),
                           visual_b_des: self.lineEdit_visual_browse_des.text()}

            des_path = des_dir_dic[call_from]

            validate_path_status = validate_path_link(des_path)

            if os.path.isdir(des_path):
                if validate_path_status[0]:
                    write_d_loc(call_from, des_path)
                    self.label_messages.setText('')
                    if call_from == visual_b_des:
                        update_history()
                else:
                    self.label_messages.setText('Save directory cannot include special character(s) ' +
                                                validate_path_status[1])
            else:
                self.label_messages.setText('Save directory does not exists ✘, please try again!')

            validate_and_update_buttons(tab)

        def browse_path(browse_call_from, tab):
            source_file_dic = {run_b_source: self.lineEdit_run_browse_source,
                               visual_b_source: self.lineEdit_visual_browse_source,
                               save_species_file: self.lineEdit_custom_file_name}

            browse_sources = [run_b_source, visual_b_source, import_seq]

            browse_des = {run_b_des: [self.lineEdit_run_browse_des, 'Save simulation outputs selected ✔'],
                          visual_b_des: [self.lineEdit_visual_browse_des, 'Save analysis outputs selected ✔']}

            win_heading_and_file_type = {web_browser_loc: ['Navigate to chrome browser', 'Chrome.exe(*.exe)'],
                                         run_b_source: ['Browse test tube', 'Species(*.species)'],
                                         visual_b_source: ['Browse Dump/Species file', 'Dump/Species(*.0 *.species)'],
                                         visual_b_des: 'Save analysis outputs',
                                         run_b_des: 'Save simulation outputs',
                                         import_seq: ['Import sequences from Dump/Species file',
                                                      'Dump/Species(*.0 *.species)'],
                                         save_species_file: ['Save test tube', 'Species(*.species)']}

            if browse_call_from in browse_sources:

                path = str(os.path.dirname(str(read_s_loc(browse_call_from))))
                file_path, _ = QFileDialog.getOpenFileName(None, win_heading_and_file_type[browse_call_from][0],
                                                           path, win_heading_and_file_type[browse_call_from][1])

                if len(file_path) > 0:
                    validate_path_status = validate_path_link(file_path)

                    if validate_path_status[0]:
                        if not browse_call_from == import_seq:
                            source_file_dic[browse_call_from].setText(file_path)

                        elif browse_call_from == import_seq:
                            validate_status = input_file_validations(file_path, browse_call_from)
                            return validate_status

                        validate_and_update_buttons(tab)

                    else:
                        self.label_messages.setText('Source path cannot include special character(s) ' +
                                                    validate_path_status[1])

            elif browse_call_from in browse_des:
                path = str(read_d_loc(browse_call_from))
                dir_path = QFileDialog.getExistingDirectory(None, win_heading_and_file_type[browse_call_from], path)

                cur_des_path = self.lineEdit_visual_browse_des.text()

                validate_path_status = validate_path_link(dir_path)

                if validate_path_status[0]:
                    if os.path.isdir(dir_path):
                        browse_des[browse_call_from][0].setText(dir_path)
                        write_d_loc(browse_call_from, dir_path)

                    elif not os.path.isdir(dir_path) and os.path.isdir(cur_des_path):
                        self.label_messages.setText('New destination folder not selected, returned to previous ✔')

                    elif not os.path.isdir(dir_path) and not os.path.isdir(cur_des_path):
                        self.label_messages.setText('Destination folder not selected ✘, please try again!')

                    update_history() if browse_call_from == visual_b_des else None
                    self.label_messages.setText(browse_des[browse_call_from][1])

                    validate_and_update_buttons(tab)

                else:
                    self.label_messages.setText('Save directory cannot include special character(s) ' +
                                                validate_path_status[1])

            elif browse_call_from == save_species_file:
                path = str(read_s_loc(browse_call_from))
                file_path = QFileDialog.getSaveFileName(None, win_heading_and_file_type[browse_call_from][0],
                                                        path, win_heading_and_file_type[browse_call_from][1])

                validate_path_status = validate_path_link(file_path)

                if validate_path_status[0]:
                    if len(file_path) > 0:
                        if file_path[0] != '':
                            if file_path[0].endswith('.species'):
                                source_file_dic[browse_call_from].setText(file_path[0])

                            else:
                                try:
                                    f_path = file_path[0].rsplit('.')[0] + '.species'
                                    source_file_dic[browse_call_from].setText(f_path)
                                except:
                                    pass

                        else:
                            self.lineEdit_custom_file_name.setText(species_file_default_path)

                        validate_and_update_buttons(tab)

                else:
                    self.label_messages.setText('Source path cannot include special character(s) ' +
                                                validate_path_status[1])

            elif browse_call_from in web_browser_loc:

                path = str(os.path.dirname(str(read_s_loc(browse_call_from))))
                file_path, _ = QFileDialog.getOpenFileName(None, win_heading_and_file_type[browse_call_from][0],
                                                           path, win_heading_and_file_type[browse_call_from][1])

                if len(file_path) > 0:
                    validate_path_status = validate_path_link(file_path)

                    if validate_path_status[0]:
                        return file_path

        @run_in_thread
        def run_visualisation(a):
            s_file_path = self.lineEdit_visual_browse_source.text()
            d_dir_path = self.lineEdit_visual_browse_des.text()
            get_adv = advanced_criteria if len(
                advanced_criteria) != 0 and self.checkBox_visual_advanced.isChecked() else None
            run = browse_and_parse_v03.open_file(s_file_path, d_dir_path, get_adv)

            if isinstance(run[0], bool):
                self.label_messages.setText(run[2] + ' file --- ' + run[1] + ' --- processed successfully ✔')
                update_history()
            elif isinstance(run[0], str):
                self.label_messages.setText(run[0])
            else:
                return None

        def pop_view(a, b):
            history_list = self.listWidget_visual_history_list
            list_all = [history_list.item(index).text() for index in range(history_list.count())]
            selection = list_all[history_list.currentRow()][3:]
            selection_link = self.lineEdit_visual_browse_des.text() + '/' + selection

            try:
                for file in os.listdir(selection_link):
                    if file.endswith(a):
                        if b == 'html':
                            f_path = selection_link + '/' + file
                            chrome_path = read_s_loc(web_browser_loc) + ' %s'
                            x = lambda: webbrowser.get(chrome_path).open_new(f_path)
                            t = threading.Thread(target=x)
                            t.start()

                        elif b == 's_sp':
                            if '_source_species' in file:
                                f_path = selection_link + '/' + file
                                os.startfile(f_path)

                        elif b == 'r_sp':
                            if '_result_species' in file:
                                f_path = selection_link + '/' + file
                                os.startfile(f_path)
            except:
                self.label_messages.setText('Some error occurred, please try again!')

        def delete_folder():
            history_list = self.listWidget_visual_history_list
            list_all = [history_list.item(index).text() for index in range(history_list.count())]
            selection = list_all[history_list.currentRow()][3:]
            selection_link = self.lineEdit_visual_browse_des.text() + '/' + selection

            folder_name = selection_link.rsplit('/', 1)[1]

            if os.path.isdir(selection_link):
                if os.path.isdir(selection_link):
                    warning = get_user_consent('delete_folder', [folder_name, ''])

                    if warning == 16384:
                        shutil.rmtree(selection_link)
                        self.label_messages.setText('Simulation outputs folder --- ' + folder_name + ' --- deleted ✔')
                        update_history()

                    else:
                        self.label_messages.setText('No changes made!')
            else:
                self.label_messages.setText('This folder does not exists anymore!')

        def create_bngl_sequence(ent):
            dna_seq = ['A', 'T', 'G', 'C']

            seq = ''.join(c.upper() for c in ent if c.upper() in dna_seq) if len(ent) != 0 else None

            if seq:
                bngl_syn = 'N(b~' + seq[0] + ',5,3!1,W,fg~0)'

                if len(seq) > 2:
                    for i in range(1, len(seq) - 1):
                        bngl_syn += '.N(b~{},5!{},3!{},W,fg~0)'.format(seq[i], str(i), str(i + 1))

                    bngl_syn += '.N(b~{},5!{},3,W,fg~0)'.format(seq[-1], str(len(seq) - 1))  # + '  ' + str(am)

                elif len(seq) == 2:
                    bngl_syn += '.N(b~{},5!{},3,W,fg~0)'.format(seq[-1], str(1))  # + '  ' + str(am)

                else:
                    self.label_messages.setText('Minimum two nucleotides required!')
                    return None

                return bngl_syn

            else:
                self.label_messages.setText('Minimum two nucleotides required!')

            validate_and_update_buttons(write_tab)

        def update_created_list():
            global ssdna_comp_list, type_dic_ssdna_comp

            if ssdna_comp_list != []:
                mx_size = len(str(max([k[1] for k in ssdna_comp_list])))
                type_dic_ssdna_comp['spaces'] = mx_size
                self.listWidget_write_list_created.clear()

                for seqs in reversed(ssdna_comp_list):
                    s_text = '{} || {}{} ||  {}'.format(type_dic_ssdna_comp[seqs[0]], seqs[1],
                                                        ' ' * int(mx_size - len(str(seqs[1]))),
                                                        seqs[2])
                    self.listWidget_write_list_created.insertItem(0, s_text)
            else:
                type_dic_ssdna_comp['spaces'] = int
                self.listWidget_write_list_created.clear()

            validate_and_update_buttons(write_tab)

        def add_sequence():
            global ssdna_comp_list

            seq = self.lineEdit_write_sequence.text()
            am = self.lineEdit_write_amount.text() or '1'

            exist_items = [e[2] for e in ssdna_comp_list]

            if seq not in exist_items:
                seq_syn = create_bngl_sequence(seq)
                ll = [1, int(am), seq, seq_syn]
                ssdna_comp_list.insert(0, ll)

            elif seq in exist_items:
                item_index = exist_items.index(seq)
                ssdna_comp_list[item_index][1] += int(am)

            update_created_list()

        def import_sequences(call_from, tab):
            global imp_seq_temp, ssdna_comp_list

            browse_get_status = browse_path(call_from, tab)

            if browse_get_status == True:
                exist_items = ['|' + e[3] + '|' for e in ssdna_comp_list]

                for ll in reversed(imp_seq_temp):
                    u_item = '|' + ll[3] + '|'
                    if u_item not in exist_items:
                        ssdna_comp_list.insert(0, ll)
                        exist_items.insert(0, u_item)

                    elif u_item in exist_items:
                        item_index = exist_items.index(u_item)
                        ssdna_comp_list[item_index][1] += ll[1]

                self.label_messages.setText('Same ssDNA(s) or Complex(es) already exists, their amounts aggregated ✔')
                imp_seq_temp = []

                update_created_list()

        def validate_char(call_from):
            seq_in_var = self.lineEdit_write_sequence
            seq_in = {write_the_seq: seq_in_var.text(), write_edit_seq: write_edited_seq_g}
            cur_seq = seq_in[call_from]
            allowed = ('A', 'T', 'C', 'G')

            def set_seq_values(v):
                global write_edited_seq_g

                if cur_seq != v:
                    if call_from == write_the_seq:
                        seq_in_var.setText(v)
                    elif call_from == write_edit_seq:
                        write_edited_seq_g = v

            new_seq = ''
            for s in cur_seq:
                if len(cur_seq) != 0:
                    if s.upper() in allowed:
                        new_seq += s.upper()

            set_seq_values(new_seq)

            if not call_from == write_edit_seq:
                validate_and_update_buttons(write_tab)

        def validate_num(call_from, tab):

            place_dic = {write_n_seq: self.lineEdit_write_amount,
                         run_start_time: self.lineEdit_run_start_time,
                         run_n_dumps: self.lineEdit_run_n_dumps,
                         run_sim_end: self.lineEdit_run_sim_end,
                         write_edit_amount: write_edited_amount_g,
                         vis_adv_ranges: vis_adv_ranges_g,
                         validate_float: validated_float_g,
                         validate_int: validated_int_g}

            child_window = [write_edit_amount, vis_adv_ranges, validate_float, validate_int]

            amount_in = str(place_dic[call_from].text()) if call_from not in child_window \
                else str(place_dic[call_from])

            only_int_type = [write_n_seq, run_n_dumps, write_edit_amount, vis_adv_ranges, validate_int]
            only_float_type = [run_start_time, run_sim_end, validate_float]

            if call_from in only_int_type:

                def set_amount_values(v):
                    global write_edited_amount_g, vis_adv_ranges_g, validated_int_g

                    if amount_in != v:
                        if call_from not in child_window:
                            place_dic[call_from].setText(v)
                        elif call_from in child_window:
                            if call_from == write_edit_amount:
                                write_edited_amount_g = v
                            elif call_from == vis_adv_ranges:
                                vis_adv_ranges_g = v
                            elif call_from == validate_int:
                                validated_int_g = v

                new_seq = ''
                if len(amount_in) >= 1:
                    for s in amount_in:
                        if s.isdigit():
                            new_seq += s

                    if len(new_seq) >= 1:
                        if int(new_seq) >= 1:
                            set_amount_values(str(int(new_seq)))
                        elif int(new_seq) == 0:
                            set_amount_values('1')
                    else:
                        set_amount_values('')

            if call_from in only_float_type:

                def set_amount_values(v):
                    global validated_float_g

                    if amount_in != v:
                        if call_from not in child_window:
                            place_dic[call_from].setText(v)
                        elif call_from in child_window:
                            validated_float_g = v

                new_seq_num = ''
                if len(amount_in) >= 1:
                    for s in amount_in:
                        if s.isdigit() or s == '.':
                            new_seq_num += s

                    coun_dots = new_seq_num.count('.')
                    new_seq_clean = ''
                    for ss in new_seq_num:
                        if ss != '.':
                            new_seq_clean += ss
                        elif ss == '.':
                            if '.' not in new_seq_clean:
                                if not coun_dots > 1:
                                    new_seq_clean += ss
                                elif coun_dots > 1:
                                    coun_dots -= 1

                    if len(new_seq_clean) == 1 and new_seq_clean == '.':
                        set_amount_values('')
                    else:
                        try:
                            new_seq_clean = int(new_seq_clean)
                        except:
                            pass

                        if not type(new_seq_clean) == int:
                            try:
                                if not new_seq_clean.startswith('.') and not new_seq_clean.endswith('.'):
                                    new_seq_clean_new = new_seq_clean.split('.')
                                    new_seq_clean = '{}.{}'.format(int(new_seq_clean_new[0]), new_seq_clean_new[1])
                                elif new_seq_clean.endswith('.'):
                                    new_seq_clean = str(int(new_seq_clean[:-1])) + '.'

                                elif new_seq_clean.startswith('.'):
                                    new_seq_clean = str(int(new_seq_clean[1:]))
                            except:
                                new_seq_clean = ''

                        set_amount_values(str(new_seq_clean))

            if call_from not in child_window:
                validate_and_update_buttons(tab)

        def save_species():
            def write_s_file(p, data):
                with open(p, 'w') as f:
                    f.write("%s" % '##### Test tube file generated by VDNA-Lab #####\n')
                    f.write("%s" % '\n')
                    for item in data:
                        line = '{}  {}\n'.format(item[3], item[1])
                        f.write("%s" % line)
                f.close()

            if not self.checkBox_custom_file_name.isChecked():
                write_s_file(species_file_system_path, ssdna_comp_list)
                self.lineEdit_run_browse_source.setText('')
                write_s_loc(run_b_source, '')

            elif self.checkBox_custom_file_name.isChecked():
                path = self.lineEdit_custom_file_name.text()
                write_s_file(path, ssdna_comp_list)
                self.lineEdit_run_browse_source.setText(path)
                write_s_loc(run_b_source, path)

            self.label_messages.setText('Test tube saved ✔')

        def write_bngl(f_path, spe_list, a):

            data, q = [], []

            with open(f_path, 'r') as f:
                l = f.readlines()
                for i in l:
                    check_syn = i.rstrip('\n').rstrip()

                    if begin_species not in q:
                        if check_syn != begin_species:
                            data.append(i)

                        elif check_syn == begin_species:
                            data.append(check_syn + '\n')
                            q.append(check_syn)
                            data.append('\n')
                            data.append('# written by VDNA ----- begin species' + '\n')
                            data.append('\n')

                            for s in spe_list:
                                data.append(s)
                                data.append('\n')

                            data.append('\n')
                            data.append('# written by VDNA ----- end species' + '\n')
                            data.append('\n')
                            q.append('done_species')

                    elif begin_species in q and 'done_species' in q and end_species not in q:
                        if check_syn != end_species and a == 'without':
                            continue

                        elif check_syn != end_species and a == 'with':
                            data.append(i)

                        elif check_syn == end_species:
                            data.append(check_syn + '\n')
                            q.append(check_syn)

                    elif begin_species in q and 'done_species' in q and end_species in q:
                        data.append(i)
            f.close()

            with open(f_path, 'w') as f:
                for item in data:
                    f.write("%s" % item)
            f.close()

        def delete_created_sequences(c_row):
            type_dic = {1: 'sequence', 2: 'complex'}
            seq = ssdna_comp_list[c_row]

            consent = get_user_consent('delete_seq_comp', [str(seq[2][:40] + ' ...'), type_dic[seq[0]]])

            if consent == 16384:
                del ssdna_comp_list[c_row]
                update_created_list()

            validate_and_update_buttons(write_tab)

        def reset_created_sequences_list():
            global ssdna_comp_list

            if get_user_consent('write_reset', ['', '']) == 16384:
                self.listWidget_write_list_created.clear()
                ssdna_comp_list = []
                self.label_messages.setText('List reset done ✔')

            validate_and_update_buttons(write_tab)

        def save_species_dir():
            checkbox_cfm_var = self.checkBox_custom_file_name
            if checkbox_cfm_var.isChecked():
                self.lineEdit_custom_file_name.setEnabled(True)
                self.pushButton_save_species_browse.setEnabled(True)
            else:
                self.lineEdit_custom_file_name.setDisabled(True)
                self.pushButton_save_species_browse.setDisabled(True)

            set_species_save_dir('')

        def get_k_values(f_p):
            data, q = {}, []
            with open(f_p, 'r') as f:
                begin_k, end_k = 'begin parameters', 'end parameters'
                l = f.readlines()
                for i in l:
                    check_syn = i.rstrip('\n').strip()

                    if begin_k not in q:
                        if check_syn != begin_k:
                            continue

                        elif check_syn == begin_k:
                            q.append(begin_k)

                    elif begin_k in q:
                        if check_syn.startswith('k'):
                            check_k = check_syn.split(' ')

                            if len(check_k) == 2:
                                if check_k[0][0] == 'k' and check_k[0][1:].isdigit():
                                    if check_k[1].isdigit():
                                        k_v = 'k' + str(check_k[0][1:])
                                        data.update({k_v: check_k[-1]})

                                    else:
                                        try:
                                            try_float = float(check_k[1])
                                            k_v = 'k' + str(check_k[0][1:])
                                            data.update({k_v: str(try_float)})
                                        except:
                                            pass
                            else:
                                continue

                        elif check_syn.startswith('Temp'):
                            check_k = check_syn.split(' ')
                            if check_k[0] == 'Temp' and check_k[-1].isdigit():
                                data.update({check_k[0]: check_k[-1]})

                            else:
                                continue

                        elif check_syn == end_k:
                            break
                        else:
                            continue
            return data

        def create_run_bngl_file():
            global run_set_source
            species_file_path = ''
            def get_spe(f_p):
                spe_list = []
                with open(f_p, 'r') as f:
                    l = f.readlines()
                    for i in l:
                        if i.startswith('N('):
                            spe_line = i.rstrip('\n').strip()
                            spe_list.append(spe_line)
                f.close()
                return spe_list

            if self.lineEdit_run_browse_source.text() != '':
                species_file_path = self.lineEdit_run_browse_source.text()

            else:
                species_file_path = species_file_system_path

            if self.checkBox_run_advanced.isChecked():
                species_list = get_spe(species_file_path)
                write_bngl(advanced_bngl_path, species_list, 'without')
                run_set_source = advanced_bngl_path

            elif not self.checkBox_run_advanced.isChecked():
                species_list = get_spe(species_file_path)
                write_bngl(bngl_file_system_path, species_list, 'without')
                run_set_source = bngl_file_system_path

        def run_bngl():
            create_run_bngl_file()
            start_time = self.lineEdit_run_start_time.text()
            end_time = self.lineEdit_run_sim_end.text()
            n_dumps = self.lineEdit_run_n_dumps.text()

            dump = {'start': start_time,
                    'period': str(round((float(end_time) / float(n_dumps)), 4)),
                    'end': end_time,
                    'steps': n_dumps}

            def get_source(s):
                file_dir_name = s.rsplit('/', 1)
                file_name_full = file_dir_name[1]
                file_name = file_dir_name[1].rsplit('.', 1)[0]
                file_type = file_dir_name[1].rsplit('.', 1)[1]
                file_name_xml = file_name + '.xml'

                file = {'file_dir': file_dir_name[0],
                        'file_name_full': file_name_full,
                        'file_name': file_name,
                        'file_type': file_type,
                        'file_name_xml': file_name_xml
                        }
                return file

            input_info = get_source(run_set_source)

            def creat_dump_folder():
                dump_dir = self.lineEdit_run_browse_des.text()

                def creat_folder(name):
                    nums = []
                    try:
                        existing = list(next(os.walk(dump_dir)))[1]
                        for i in existing:
                            n_num = i.rsplit('--', 1)
                            if name == n_num[0]:
                                nums.append(int(n_num[1]))
                    except:
                        pass

                    new_name = name + '--' + (str(max(nums) + 1) if nums != [] else '1')
                    return new_name

                dump_folder_name = creat_folder(input_info['file_name'])
                dump_dir = dump_dir.replace('/', '\\') + '\\' + dump_folder_name

                return {'dump_dir': dump_dir, 'dump_folder_name': dump_folder_name}

            dump_info = creat_dump_folder()

            def convert_link_address(d):
                chars = ['\\', '/', '_', ':', '-', '.']
                dir = ''

                for c in d:
                    if c.isalpha() or c.isdigit() or c in chars:
                        dir += c
                    else:
                        dir += '^' + c
                return dir

            local_path = os.path.abspath(__file__).rsplit('\\', 2)[0]
            input_file_path_raw = input_info['file_dir'].replace('/', '\\')
            dump_dir_path_converted = convert_link_address(dump_info['dump_dir'])
            dump_dir_path_for_rnf = dump_info['dump_dir'] + '/'

            nfsim_pl_path_converted = convert_link_address(local_path + '\\NFsim_v1.11\\bng2.pl')
            nfsim_exe_path_converted = convert_link_address(local_path + '\\NFsim_v1.11\\bin\\NFsim_MSWin32.exe')
            perl_path_converted = convert_link_address(local_path + '\\Perl64\\bin\\perl.exe')

            input_file_bngl = '{}\\{}'.format(input_file_path_raw, input_info['file_name_full'])
            input_file_xml = '{}\\{}'.format(input_file_path_raw, input_info['file_name_xml'])
            run_period = '[{}:{}:{}]'.format(dump['start'], dump['period'], dump['end'])

            com_change_dir = '"CD "{}\\"'.format(convert_link_address(input_file_path_raw))
            com_make_xml = '"{}" "{}" -xml "{}"'.format(perl_path_converted,
                                                        nfsim_pl_path_converted,
                                                        convert_link_address(input_file_bngl))
            com_make_dump_dir = 'md "{}\\"'.format(dump_dir_path_converted)
            com_run_nfsim_basic = '"{}" -utl 1000 -xml "{}" -dump "{}-^>{}/" -oSteps {} -sim {}"'.format(
                nfsim_exe_path_converted,
                convert_link_address(input_file_xml),
                run_period,
                dump_dir_path_converted,
                dump['steps'],
                end_time)

            main_run_command = 'START CMD /K {} && {} && {}'.format(com_change_dir,
                                                                    com_make_xml,
                                                                    com_make_dump_dir)

            run_rnf_data_dic = {'input_file_name': input_info['file_name'],
                                'input_file_path_raw': input_file_path_raw,
                                'dump_dir_path': dump_dir_path_for_rnf}

            def run_sim_on_thread(cmd_com):
                x = lambda: os.system(cmd_com)
                t = threading.Thread(target=x)
                t.start()
                self.label_messages.setText('Processing data on CMD!')

            if self.checkBox_run_advanced.isChecked() and run_kt_g and run_annealing_g:
                make_rnf = make_rnf_file(run_kt_list_g, run_rnf_data_dic, run_temper_data_g, run_time_data_g)
                com_run_rnf = '"{}" -rnf "{}"'.format(nfsim_exe_path_converted, convert_link_address(make_rnf))
                cmd_command = '{} && {}'.format(main_run_command,
                                                com_run_rnf)

                run_sim_on_thread(cmd_command)

            elif self.checkBox_run_advanced.isChecked() and run_kt_g and not run_annealing_g:
                run_time_data_basic = [dump['start'], dump['period'], '', dump['end']]
                make_rnf = make_rnf_file(run_kt_list_g, run_rnf_data_dic, False, run_time_data_basic)
                com_run_rnf = '"{}" -rnf "{}"'.format(nfsim_exe_path_converted, convert_link_address(make_rnf))
                cmd_command = '{} && {}'.format(main_run_command,
                                                com_run_rnf)

                run_sim_on_thread(cmd_command)

            else:
                cmd_command = '{} && {}'.format(main_run_command,
                                                com_run_nfsim_basic)

                run_sim_on_thread(cmd_command)

        def advanced_options():
            global p_o_n

            p_o_n = 0

            def get_add_criteria():
                range_from, range_to, unbound_from, unbound_to, criteria_list = lineEdit_range_from, \
                                                                                lineEdit_range_to, \
                                                                                lineEdit_unbound_from, \
                                                                                lineEdit_unbound_to, \
                                                                                listWidget_list_criteria
                l_dummy = [None, None, None, None, None, False]
                l_display = ''
                p_o_n_dic = {0: ['%', '0%', '100%', '%'], 1: ['n', 'Min.', 'Max.', '']}
                amount_from_item = range_from.text()
                amount_to_item = range_to.text()
                unbound_from_item = unbound_from.text()
                unbound_to_item = unbound_to.text()
                # p_o_n = p_or_n.text()
                range_text = 'ssDNA(s) range, from {} to {}'.format(
                    amount_from_item if amount_from_item else 'Min.',
                    amount_to_item if amount_to_item else 'Max.')

                if amount_from_item != '' or amount_to_item != '':
                    l_dummy[0] = amount_from_item
                    l_dummy[1] = amount_to_item

                if unbound_from_item != '' or unbound_to_item != '':
                    pon = p_o_n_dic[p_o_n]
                    l_dummy[2] = unbound_from_item
                    l_dummy[3] = unbound_to_item
                    l_dummy[4] = pon[0]
                    l_d_p = 'Unbound {}, from {} to {}'.format(pon[0], unbound_from_item + pon[3]
                    if unbound_from_item != '' else pon[1],
                                                               unbound_to_item + pon[3]
                                                               if unbound_to_item != '' else pon[2])
                    l_display = l_d_p

                new_item = '✅  {}{}'.format(range_text, '  |  ' + l_display if l_display != '' else '')

                return [l_dummy, new_item]

            def update_add_button():

                item = get_add_criteria()
                list_var = listWidget_list_criteria
                existing = [list_var.item(index).text() for index in range(list_var.count())]

                if item[0][0] or item[0][1]:
                    current_range_from = int(item[0][0]) if item[0][0] else 1
                    current_range_to = int(item[0][1]) if item[0][1] else float('inf')

                    if current_range_from <= current_range_to:
                        check_if_exists = item[1] in [i[:-14] if i.endswith('Highlighted') else i for i in existing]
                        if not item[0][2] and not item[0][3]:
                            if not check_if_exists:
                                pushButton_add_parameter.setEnabled(True)
                            else:
                                pushButton_add_parameter.setDisabled(True)

                        elif item[0][2] or item[0][3]:
                            unb_from_n = int(item[0][2]) if item[0][2] else 0
                            unb_to_n = int(item[0][3]) if item[0][3] else 100 if item[0][4] == '%' else float('inf')
                            if unb_from_n <= unb_to_n:
                                if not check_if_exists:
                                    pushButton_add_parameter.setEnabled(True)
                                else:
                                    pushButton_add_parameter.setDisabled(True)
                            else:
                                pushButton_add_parameter.setDisabled(True)
                        else:
                            pushButton_add_parameter.setDisabled(True)
                    else:
                        pushButton_add_parameter.setDisabled(True)
                else:
                    pushButton_add_parameter.setDisabled(True)

            def validate_filter_input(place_id):

                place_dic = {'range_from': lineEdit_range_from,
                             'range_to': lineEdit_range_to,
                             'unbound_from': lineEdit_unbound_from,
                             'unbound_to': lineEdit_unbound_to,
                             'radio_button': ''}
                item_now = place_dic[place_id]

                if place_id == 'range_from' or place_id == 'range_to':
                    global vis_adv_ranges_g

                    vis_adv_ranges_g = item_now.text()
                    validate_num(vis_adv_ranges, '')
                    if item_now.text() != vis_adv_ranges_g:
                        item_now.setText(vis_adv_ranges_g)

                elif place_id == 'unbound_from' or place_id == 'unbound_to':
                    if len(str(item_now.text())) >= 1:
                        try:
                            if type(int(item_now.text())) == int:
                                int_type = int(item_now.text())
                                if p_o_n == 0:
                                    if int_type == 0:
                                        item_now.setText('0')
                                    elif 0 < int_type <= 100:
                                        item_now.setText(str(int_type))
                                    elif int_type > 100:
                                        item_now.setText('100')
                                elif p_o_n == 1:
                                    if 0 < int_type:
                                        item_now.setText(str(int_type))
                        except:
                            item_now.setText('')

                elif place_id == 'radio_button':
                    if p_o_n == 0:
                        try:
                            if int(place_dic['unbound_from'].text()) > 100:
                                place_dic['unbound_from'].setText('100')
                        except:
                            pass
                        try:
                            if int(place_dic['unbound_to'].text()) > 100:
                                place_dic['unbound_to'].setText('100')
                        except:
                            pass

                update_add_button()

            def highlight_criteria(a):
                criteria_list_var = listWidget_list_criteria
                criteria_list = [criteria_list_var.item(index).text() for index in range(criteria_list_var.count())]
                selection = criteria_list[a]
                highlight_item = selection + ' - Highlighted'
                check_highlight = len([i.endswith('Highlighted') for i in criteria_list]) == 0
                highlight_cleaned = []

                for item in criteria_list:
                    if item.endswith('Highlighted'):
                        highlight_cleaned.append(item[:-14])
                    else:
                        highlight_cleaned.append(item)

                if not selection.endswith('Highlighted'):
                    if not check_highlight:
                        highlight_cleaned[a] = highlight_item
                        criteria_list_var.clear()
                        for h in highlight_cleaned:
                            criteria_list_var.insertItem(len(criteria_list), h)
                            pushButton_highlight_parameter.setDisabled(True)

                    elif check_highlight:
                        criteria_list[a] = highlight_item
                        criteria_list_var.clear()
                        for h in criteria_list:
                            criteria_list_var.insertItem(len(criteria_list), h)
                            pushButton_highlight_parameter.setDisabled(True)

                if selection.endswith('Highlighted'):
                    criteria_list_var.clear()
                    for h in highlight_cleaned:
                        criteria_list_var.insertItem(len(criteria_list), h)
                        pushButton_highlight_parameter.setText("Highlight")
                        pushButton_highlight_parameter.setDisabled(True)

                update_buttons('')

            def update_buttons(c_row):
                criteria_list_var = listWidget_list_criteria
                criteria_list = [criteria_list_var.item(index).text() for index in range(criteria_list_var.count())]
                selection = criteria_list[c_row] if c_row != '' else None

                if selection != None:
                    check_highlight = len([i.endswith('Highlighted') for i in criteria_list]) == 0
                    pushButton_delete_parameter.setEnabled(True)

                    if not check_highlight:
                        if not selection.endswith('Highlighted'):
                            pushButton_highlight_parameter.setEnabled(True)

                        elif selection.endswith('Highlighted'):
                            pushButton_highlight_parameter.setText("Un-highlight")
                            pushButton_highlight_parameter.setEnabled(True)

                    if not selection.endswith('Highlighted'):
                        pushButton_highlight_parameter.setText("Highlight")
                        pushButton_highlight_parameter.setEnabled(True)

                else:
                    pushButton_delete_parameter.setDisabled(True)
                    pushButton_highlight_parameter.setDisabled(True)

                if criteria_list != []:
                    buttonBox.setEnabled(True)
                    pushButton_reset_parameter.setEnabled(True)

                elif criteria_list == []:
                    buttonBox.setDisabled(True)
                    pushButton_reset_parameter.setDisabled(True)

            def add_criteria():
                item = get_add_criteria()[1]
                listWidget_list_criteria.insertItem(0, item)

                pushButton_add_parameter.setDisabled(True)
                update_buttons('')

            def set_ok():
                global advanced_criteria, advanced_criteria_text

                def convert_adv_criteria(d):
                    l_dummy = [None, None, None, None, None, False]

                    if 'Highlighted' in d:
                        l_dummy[5] = True

                    if '|' in d:
                        ran_un = d.split('|')
                        ran = ran_un[0][1:].split()
                        un = ran_un[1].split()
                        l_dummy[0] = int(ran[3]) if ran[3] != 'Min.' else None
                        l_dummy[1] = int(ran[5]) if ran[5] != 'Max.' else None
                        l_dummy[2] = int(un[3].strip('%')) if un[3] != 'Min.' else None
                        l_dummy[3] = int(un[5].strip('%')) if un[5] != 'Max.' else None
                        l_dummy[4] = un[1][:-1]

                    else:
                        ran = d[3:].split()
                        l_dummy[0] = int(ran[3]) if ran[3] != 'Min.' else None
                        l_dummy[1] = int(ran[5]) if ran[5] != 'Max.' else None

                    return l_dummy

                list_var = listWidget_list_criteria
                get_all = [list_var.item(index).text() for index in range(list_var.count())]

                del advanced_criteria_text[:]
                del advanced_criteria[:]

                adv_unsorted = []
                for c in get_all:
                    advanced_criteria_text.append(c)
                    cleaned = convert_adv_criteria(c)
                    adv_unsorted.append(cleaned)

                advanced_criteria = sorted(adv_unsorted, key=lambda x: x[5])
                self.checkBox_visual_advanced.setChecked(True)

            def delete_selected(c_row):
                criteria_list_var = listWidget_list_criteria
                criteria_list = [criteria_list_var.item(index).text() for index in range(criteria_list_var.count())]
                del criteria_list[c_row]
                listWidget_list_criteria.clear()
                for item in reversed(criteria_list):
                    listWidget_list_criteria.insertItem(0, item)

                update_add_button()
                update_buttons('')

            def reset_criteria_list():
                global advanced_criteria, advanced_criteria_text

                def get_user_consent_adv_run(consent_for):
                    consent_check = QMessageBox()
                    con_dic = {'reset_criteria_list': 'Resetting will remove all created criteria. '
                                                      'This action cannot be undone!' +
                                                      '\n' + '\n' +
                                                      'Click "Yes" to reset for a fresh start\n'
                                                      'Click "No" to return back', }

                    consent_check.setWindowTitle('Warning!')
                    consent_check.setText(con_dic[consent_for])
                    consent_check.setStandardButtons(
                        QMessageBox.Yes | QMessageBox.No)
                    consent = consent_check.exec_()

                    return consent

                consent = get_user_consent_adv_run('reset_criteria_list')

                if consent == 16384:
                    listWidget_list_criteria.clear()

                    advanced_criteria, advanced_criteria_text = [], []
                    self.checkBox_visual_advanced.setChecked(False)

                    update_buttons('')
                    update_add_button()

            def set_radio_status():
                global p_o_n
                checked_item = {1: radioButton_number.isChecked(),
                                0: radioButton_percentage.isChecked()}
                a = [i for i, status in checked_item.items() if status]
                p_o_n = a[0]
                validate_filter_input('radio_button')
                update_add_button()

            def set_existing_parameters():
                if advanced_criteria_text != []:
                    for item in reversed(advanced_criteria_text):
                        listWidget_list_criteria.insertItem(0, item)

                    update_buttons('')

            visual_adv_dialog = QDialog()
            visual_adv_dialog.setObjectName("Dialog")
            visual_adv_dialog.setEnabled(True)
            visual_adv_dialog.resize(800, 350)
            sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(visual_adv_dialog.sizePolicy().hasHeightForWidth())
            visual_adv_dialog.setSizePolicy(sizePolicy)
            visual_adv_dialog.setMaximumSize(QSize(900, 405))
            gridLayout_3 = QGridLayout(visual_adv_dialog)
            gridLayout_3.setObjectName("gridLayout_3")
            frame_5 = QFrame(visual_adv_dialog)
            sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(frame_5.sizePolicy().hasHeightForWidth())
            frame_5.setSizePolicy(sizePolicy)
            frame_5.setFrameShape(QFrame.StyledPanel)
            frame_5.setFrameShadow(QFrame.Raised)
            frame_5.setObjectName("frame_5")
            gridLayout = QGridLayout(frame_5)
            gridLayout.setContentsMargins(20, 20, 20, 20)
            gridLayout.setObjectName("gridLayout")
            gridLayout_2 = QGridLayout()
            gridLayout_2.setObjectName("gridLayout_2")
            horizontalLayout = QHBoxLayout()
            horizontalLayout.setObjectName("horizontalLayout")
            label_ssDNA_range = QLabel(frame_5)
            sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(label_ssDNA_range.sizePolicy().hasHeightForWidth())
            label_ssDNA_range.setSizePolicy(sizePolicy)
            label_ssDNA_range.setObjectName("label_ssDNA_range")
            horizontalLayout.addWidget(label_ssDNA_range)
            lineEdit_range_from = QLineEdit(frame_5)
            font = QFont()
            font.setPointSize(9)
            lineEdit_range_from.setFont(font)
            lineEdit_range_from.setObjectName("lineEdit_range_from")
            horizontalLayout.addWidget(lineEdit_range_from)
            label_2 = QLabel(frame_5)
            label_2.setObjectName("label_2")
            horizontalLayout.addWidget(label_2)
            lineEdit_range_to = QLineEdit(frame_5)
            font = QFont()
            font.setPointSize(9)
            lineEdit_range_to.setFont(font)
            lineEdit_range_to.setObjectName("lineEdit_range_to")
            horizontalLayout.addWidget(lineEdit_range_to)
            label_5 = QLabel(frame_5)
            font = QFont()
            font.setPointSize(12)
            font.setBold(True)
            font.setUnderline(False)
            font.setWeight(75)
            font.setKerning(True)
            label_5.setFont(font)
            label_5.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignTop)
            label_5.setObjectName("label_5")
            horizontalLayout.addWidget(label_5)
            label_unbound = QLabel(frame_5)
            label_unbound.setObjectName("label_unbound")
            horizontalLayout.addWidget(label_unbound)
            radioButton_percentage = QRadioButton(frame_5)
            radioButton_percentage.setObjectName("radioButton_percentage")
            horizontalLayout.addWidget(radioButton_percentage)
            radioButton_number = QRadioButton(frame_5)
            radioButton_number.setObjectName("radioButton_number")
            horizontalLayout.addWidget(radioButton_number)
            lineEdit_unbound_from = QLineEdit(frame_5)
            font = QFont()
            font.setPointSize(9)
            lineEdit_unbound_from.setFont(font)
            lineEdit_unbound_from.setObjectName("lineEdit_unbound_from")
            horizontalLayout.addWidget(lineEdit_unbound_from)
            label_3 = QLabel(frame_5)
            label_3.setObjectName("label_3")
            horizontalLayout.addWidget(label_3)
            lineEdit_unbound_to = QLineEdit(frame_5)
            font = QFont()
            font.setPointSize(9)
            lineEdit_unbound_to.setFont(font)
            lineEdit_unbound_to.setObjectName("lineEdit_unbound_to")
            horizontalLayout.addWidget(lineEdit_unbound_to)
            pushButton_add_parameter = QPushButton(frame_5)
            pushButton_add_parameter.setObjectName("pushButton_add_parameter")
            horizontalLayout.addWidget(pushButton_add_parameter)
            gridLayout_2.addLayout(horizontalLayout, 0, 0, 1, 1)
            frame = QFrame(frame_5)
            frame.setMinimumSize(QSize(0, 15))
            frame.setFrameShape(QFrame.StyledPanel)
            frame.setFrameShadow(QFrame.Raised)
            frame.setObjectName("frame")
            gridLayout_2.addWidget(frame, 1, 0, 1, 1)
            gridLayout_parameters = QGridLayout()
            gridLayout_parameters.setContentsMargins(-1, 0, -1, -1)
            gridLayout_parameters.setObjectName("gridLayout_parameters")
            listWidget_list_criteria = QListWidget(frame_5)
            listWidget_list_criteria.setMinimumSize(QSize(0, 150))
            listWidget_list_criteria.setObjectName("listWidget_list_criteria")
            gridLayout_parameters.addWidget(listWidget_list_criteria, 0, 0, 7, 1)
            pushButton_highlight_parameter = QPushButton(frame_5)
            pushButton_highlight_parameter.setObjectName("pushButton_highlight_parameter")
            gridLayout_parameters.addWidget(pushButton_highlight_parameter, 1, 1, 1, 1)
            frame_6 = QFrame(frame_5)
            frame_6.setFrameShape(QFrame.StyledPanel)
            frame_6.setFrameShadow(QFrame.Raised)
            frame_6.setObjectName("frame_6")
            gridLayout_parameters.addWidget(frame_6, 6, 1, 1, 1)
            pushButton_reset_parameter = QPushButton(frame_5)
            pushButton_reset_parameter.setObjectName("pushButton_reset_parameter")
            gridLayout_parameters.addWidget(pushButton_reset_parameter, 5, 1, 1, 1)
            frame_4 = QFrame(frame_5)
            frame_4.setFrameShape(QFrame.StyledPanel)
            frame_4.setFrameShadow(QFrame.Raised)
            frame_4.setObjectName("frame_4")
            gridLayout_parameters.addWidget(frame_4, 4, 1, 1, 1)
            frame_3 = QFrame(frame_5)
            frame_3.setFrameShape(QFrame.StyledPanel)
            frame_3.setFrameShadow(QFrame.Raised)
            frame_3.setObjectName("frame_3")
            gridLayout_parameters.addWidget(frame_3, 2, 1, 1, 1)
            pushButton_delete_parameter = QPushButton(frame_5)
            pushButton_delete_parameter.setObjectName("pushButton_delete_parameter")
            gridLayout_parameters.addWidget(pushButton_delete_parameter, 3, 1, 1, 1)
            frame_7 = QFrame(frame_5)
            frame_7.setFrameShape(QFrame.StyledPanel)
            frame_7.setFrameShadow(QFrame.Raised)
            frame_7.setObjectName("frame_7")
            gridLayout_parameters.addWidget(frame_7, 0, 1, 1, 1)
            gridLayout_2.addLayout(gridLayout_parameters, 2, 0, 1, 1)
            frame_2 = QFrame(frame_5)
            frame_2.setMinimumSize(QSize(0, 15))
            frame_2.setFrameShape(QFrame.StyledPanel)
            frame_2.setFrameShadow(QFrame.Raised)
            frame_2.setObjectName("frame_2")
            gridLayout_2.addWidget(frame_2, 3, 0, 1, 1)
            horizontalLayout_ok_cancel = QHBoxLayout()
            horizontalLayout_ok_cancel.setObjectName("horizontalLayout_ok_cancel")
            buttonBox = QDialogButtonBox(frame_5)
            buttonBox.setOrientation(Qt.Horizontal)
            buttonBox.setStandardButtons(QDialogButtonBox.Ok)
            buttonBox.setObjectName("buttonBox")
            horizontalLayout_ok_cancel.addWidget(buttonBox)
            pushButton_visual_cancel = QPushButton(frame_5)
            pushButton_visual_cancel.setObjectName("pushButton_visual_cancel")
            horizontalLayout_ok_cancel.addWidget(pushButton_visual_cancel)
            gridLayout_2.addLayout(horizontalLayout_ok_cancel, 4, 0, 1, 1)
            gridLayout.addLayout(gridLayout_2, 0, 0, 1, 1)
            gridLayout_3.addWidget(frame_5, 0, 0, 1, 1)

            def retranslateUi(Dialog):
                _translate = QCoreApplication.translate
                Dialog.setWindowTitle(_translate("Dialog", "Advanced filtering"))
                label_ssDNA_range.setText(_translate("Dialog", "ssDNA(s) range from"))
                label_2.setText(_translate("Dialog", "to"))
                label_5.setText(_translate("Dialog", "|"))
                label_unbound.setText(_translate("Dialog", "Unbound"))
                radioButton_percentage.setText(_translate("Dialog", "%"))
                radioButton_number.setText(_translate("Dialog", "n"))
                label_3.setText(_translate("Dialog", "to"))
                pushButton_add_parameter.setText(_translate("Dialog", "Add"))
                pushButton_highlight_parameter.setText(_translate("Dialog", "Highlight"))
                pushButton_reset_parameter.setText(_translate("Dialog", "Reset all"))
                pushButton_delete_parameter.setText(_translate("Dialog", "Delete"))
                pushButton_visual_cancel.setText(_translate("Dialog", "Cancel"))

            retranslateUi(visual_adv_dialog)
            buttonBox.accepted.connect(visual_adv_dialog.accept)
            buttonBox.rejected.connect(visual_adv_dialog.reject)

            def close_dialog():
                visual_adv_dialog.reject()

            pushButton_add_parameter.clicked.connect(add_criteria)
            radioButton_number.clicked.connect(set_radio_status)
            radioButton_percentage.clicked.connect(set_radio_status)
            radioButton_percentage.setChecked(True)
            pushButton_add_parameter.setDisabled(True)
            lineEdit_range_from.textChanged.connect(lambda: validate_filter_input('range_from'))
            lineEdit_range_to.textChanged.connect(lambda: validate_filter_input('range_to'))
            lineEdit_unbound_from.textChanged.connect(lambda: validate_filter_input('unbound_from'))
            lineEdit_unbound_to.textChanged.connect(lambda: validate_filter_input('unbound_to'))
            listWidget_list_criteria.itemClicked.connect(lambda: update_buttons(listWidget_list_criteria.currentRow()))
            pushButton_highlight_parameter.clicked.connect(lambda:
                                                           highlight_criteria(listWidget_list_criteria.currentRow()))
            buttonBox.setDisabled(True)
            pushButton_delete_parameter.setDisabled(True)
            pushButton_highlight_parameter.setDisabled(True)
            pushButton_reset_parameter.setDisabled(True)
            pushButton_delete_parameter.clicked.connect(lambda: delete_selected(listWidget_list_criteria.currentRow()))
            pushButton_reset_parameter.clicked.connect(reset_criteria_list)
            pushButton_visual_cancel.clicked.connect(close_dialog)
            set_existing_parameters() if advanced_criteria_text != [] else None
            visualize_advanced = visual_adv_dialog.exec_()

            if visualize_advanced == 1:
                set_ok()

        def edit_seq(c_row):
            to_be_edited_seq = ssdna_comp_list[c_row][2]
            to_be_edited_amount = str(ssdna_comp_list[c_row][1])
            to_be_edited_type = ssdna_comp_list[c_row][0]

            def update_edit_buttons():
                seqs_in = lineEdit_write_edit_sequence.text()
                amount_in = lineEdit_write_edit_amount.text()

                if to_be_edited_type == 1:
                    exist_items = [e[2] for e in ssdna_comp_list]
                    del exist_items[c_row]

                    if seqs_in != '' and amount_in != '':
                        if seqs_in != to_be_edited_seq or amount_in != to_be_edited_amount:
                            if len(seqs_in) >= 2 and len(amount_in) >= 1:
                                if seqs_in not in exist_items:
                                    buttonBox_write_edit.setEnabled(True)
                                else:
                                    buttonBox_write_edit.setDisabled(True)
                            else:
                                buttonBox_write_edit.setDisabled(True)
                        else:
                            buttonBox_write_edit.setDisabled(True)
                    else:
                        buttonBox_write_edit.setDisabled(True)

                elif to_be_edited_type == 2:
                    if amount_in != '':
                        if amount_in != to_be_edited_amount:
                            if len(amount_in) >= 1:
                                buttonBox_write_edit.setEnabled(True)
                            else:
                                buttonBox_write_edit.setDisabled(True)
                        else:
                            buttonBox_write_edit.setDisabled(True)
                    else:
                        buttonBox_write_edit.setDisabled(True)
                else:
                    buttonBox_write_edit.setDisabled(True)

            def save_edited_seq(item_row, edited_seq, edited_seq_amount):
                global ssdna_comp_list

                seq_syn = create_bngl_sequence(edited_seq) if to_be_edited_seq != edited_seq \
                    else ssdna_comp_list[item_row][3]
                get_edited = [to_be_edited_type, int(edited_seq_amount), edited_seq, seq_syn]
                ssdna_comp_list[item_row] = get_edited

                update_created_list()

                return True

            def set_validated(call_from):
                global write_edited_amount_g, write_edited_seq_g
                if call_from == write_edit_amount:
                    write_edited_amount_g = lineEdit_write_edit_amount.text()
                    validate_num(call_from, '')
                    if lineEdit_write_edit_amount.text() != write_edited_amount_g:
                        lineEdit_write_edit_amount.setText(write_edited_amount_g)

                elif call_from == write_edit_seq:
                    write_edited_seq_g = lineEdit_write_edit_sequence.text()
                    validate_char(call_from)
                    if lineEdit_write_edit_sequence.text() != write_edited_seq_g:
                        lineEdit_write_edit_sequence.setText(write_edited_seq_g)

                update_edit_buttons()

            write_edit_seq_dialog = QDialog()
            write_edit_seq_dialog.setObjectName("Dialog")
            write_edit_seq_dialog.resize(926, 162)
            write_edit_seq_dialog.setMaximumSize(QSize(1157, 202))
            gridLayout_2 = QGridLayout(write_edit_seq_dialog)
            gridLayout_2.setObjectName("gridLayout_2")
            frame_2 = QFrame(write_edit_seq_dialog)
            frame_2.setFrameShape(QFrame.StyledPanel)
            frame_2.setFrameShadow(QFrame.Raised)
            frame_2.setObjectName("frame_2")
            gridLayout = QGridLayout(frame_2)
            gridLayout.setObjectName("gridLayout")
            verticalLayout = QVBoxLayout()
            verticalLayout.setObjectName("verticalLayout")
            gridLayout_write_edit_sequence_entry = QGridLayout()
            gridLayout_write_edit_sequence_entry.setObjectName("gridLayout_write_edit_sequence_entry")
            frame_32 = QFrame(frame_2)
            frame_32.setFrameShape(QFrame.StyledPanel)
            frame_32.setFrameShadow(QFrame.Raised)
            frame_32.setObjectName("frame_32")
            gridLayout_write_edit_sequence_entry.addWidget(frame_32, 2, 0, 1, 1)
            frame_8 = QFrame(frame_2)
            frame_8.setFrameShape(QFrame.StyledPanel)
            frame_8.setFrameShadow(QFrame.Raised)
            frame_8.setObjectName("frame_8")
            gridLayout_write_edit_sequence_entry.addWidget(frame_8, 0, 2, 1, 1)
            frame_30 = QFrame(frame_2)
            frame_30.setFrameShape(QFrame.StyledPanel)
            frame_30.setFrameShadow(QFrame.Raised)
            frame_30.setObjectName("frame_30")
            gridLayout_write_edit_sequence_entry.addWidget(frame_30, 2, 2, 1, 1)
            frame_7 = QFrame(frame_2)
            frame_7.setFrameShape(QFrame.StyledPanel)
            frame_7.setFrameShadow(QFrame.Raised)
            frame_7.setObjectName("frame_7")
            gridLayout_write_edit_sequence_entry.addWidget(frame_7, 0, 1, 1, 1)
            label_write_edit_amount = QLabel(frame_2)
            sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(label_write_edit_amount.sizePolicy().hasHeightForWidth())
            label_write_edit_amount.setSizePolicy(sizePolicy)
            label_write_edit_amount.setAlignment(Qt.AlignCenter)
            label_write_edit_amount.setObjectName("label_write_edit_amount")
            gridLayout_write_edit_sequence_entry.addWidget(label_write_edit_amount, 0, 4, 1, 1)
            label_write_edit_allowed_num = QLabel(frame_2)
            font = QFont()
            font.setPointSize(8)
            font.setItalic(True)
            label_write_edit_allowed_num.setFont(font)
            label_write_edit_allowed_num.setAlignment(Qt.AlignCenter)
            label_write_edit_allowed_num.setObjectName("label_write_edit_allowed_num")
            gridLayout_write_edit_sequence_entry.addWidget(label_write_edit_allowed_num, 2, 4, 1, 1)
            label_write_edit_sequence = QLabel(frame_2)
            sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(label_write_edit_sequence.sizePolicy().hasHeightForWidth())
            label_write_edit_sequence.setSizePolicy(sizePolicy)
            label_write_edit_sequence.setAlignment(
                Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter)
            label_write_edit_sequence.setObjectName("label_write_edit_sequence")
            gridLayout_write_edit_sequence_entry.addWidget(label_write_edit_sequence, 0, 0, 1, 1)
            label_write_edit_allowed_char = QLabel(frame_2)
            font = QFont()
            font.setPointSize(8)
            font.setItalic(True)
            label_write_edit_allowed_char.setFont(font)
            label_write_edit_allowed_char.setAlignment(Qt.AlignCenter)
            label_write_edit_allowed_char.setObjectName("label_write_edit_allowed_char")
            gridLayout_write_edit_sequence_entry.addWidget(label_write_edit_allowed_char, 2, 1, 1, 1)
            lineEdit_write_edit_amount = QLineEdit(frame_2)
            sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(lineEdit_write_edit_amount.sizePolicy().hasHeightForWidth())
            lineEdit_write_edit_amount.setSizePolicy(sizePolicy)
            font = QFont()
            font.setPointSize(9)
            lineEdit_write_edit_amount.setFont(font)
            lineEdit_write_edit_amount.setAlignment(Qt.AlignCenter)
            lineEdit_write_edit_amount.setObjectName("lineEdit_write_edit_amount")
            gridLayout_write_edit_sequence_entry.addWidget(lineEdit_write_edit_amount, 1, 4, 1, 1)
            frame_3 = QFrame(frame_2)
            frame_3.setFrameShape(QFrame.StyledPanel)
            frame_3.setFrameShadow(QFrame.Raised)
            frame_3.setObjectName("frame_3")
            gridLayout_write_edit_sequence_entry.addWidget(frame_3, 0, 3, 1, 1)
            lineEdit_write_edit_sequence = QLineEdit(frame_2)
            sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(lineEdit_write_edit_sequence.sizePolicy().hasHeightForWidth())
            lineEdit_write_edit_sequence.setSizePolicy(sizePolicy)
            font = QFont()
            font.setPointSize(9)
            lineEdit_write_edit_sequence.setFont(font)
            lineEdit_write_edit_sequence.setObjectName("lineEdit_write_edit_sequence")
            gridLayout_write_edit_sequence_entry.addWidget(lineEdit_write_edit_sequence, 1, 0, 1, 4)
            frame_4 = QFrame(frame_2)
            frame_4.setFrameShape(QFrame.StyledPanel)
            frame_4.setFrameShadow(QFrame.Raised)
            frame_4.setObjectName("frame_4")
            gridLayout_write_edit_sequence_entry.addWidget(frame_4, 2, 3, 1, 1)
            verticalLayout.addLayout(gridLayout_write_edit_sequence_entry)
            frame = QFrame(frame_2)
            frame.setMinimumSize(QSize(0, 15))
            frame.setFrameShape(QFrame.StyledPanel)
            frame.setFrameShadow(QFrame.Raised)
            frame.setObjectName("frame")
            verticalLayout.addWidget(frame)
            horizontalLayout_save_cancel = QHBoxLayout()
            horizontalLayout_save_cancel.setObjectName("horizontalLayout_save_cancel")
            buttonBox_write_edit = QDialogButtonBox(frame_2)
            buttonBox_write_edit.setOrientation(Qt.Horizontal)
            buttonBox_write_edit.setStandardButtons(QDialogButtonBox.Save)
            buttonBox_write_edit.setObjectName("buttonBox_write_edit")
            horizontalLayout_save_cancel.addWidget(buttonBox_write_edit)
            pushButton_cancel = QPushButton(frame_2)
            pushButton_cancel.setObjectName("pushButton_cancel")
            horizontalLayout_save_cancel.addWidget(pushButton_cancel)
            verticalLayout.addLayout(horizontalLayout_save_cancel)
            gridLayout.addLayout(verticalLayout, 0, 0, 1, 1)
            gridLayout_2.addWidget(frame_2, 1, 0, 1, 1)
            buttonBox_write_edit.setDisabled(True)

            def retranslateUi(Dialog):
                _translate = QCoreApplication.translate
                Dialog.setWindowTitle(_translate("Dialog", "Edit sequence"))
                label_write_edit_amount.setText(_translate("Dialog", "Amount"))
                label_write_edit_allowed_num.setText(_translate("Dialog", "Numericals only"))
                label_write_edit_sequence.setText(_translate("Dialog", "Edit ssDNA sequence"))
                label_write_edit_allowed_char.setText(_translate("Dialog", "Allowed characters (A, T, C, G)"))
                pushButton_cancel.setText(_translate("Dialog", "Cancel"))
                # QMetaObject.connectSlotsByName(write_edit_seq_dialog)

            def close_dialog():
                write_edit_seq_dialog.reject()

            retranslateUi(write_edit_seq_dialog)
            buttonBox_write_edit.accepted.connect(write_edit_seq_dialog.accept)
            buttonBox_write_edit.rejected.connect(write_edit_seq_dialog.reject)
            write_edited_amount_g = lineEdit_write_edit_amount

            lineEdit_write_edit_sequence.setText(to_be_edited_seq)
            lineEdit_write_edit_amount.setText(to_be_edited_amount)
            lineEdit_write_edit_amount.textChanged.connect(lambda: set_validated(write_edit_amount))
            lineEdit_write_edit_sequence.textChanged.connect(lambda: set_validated(write_edit_seq))
            pushButton_cancel.clicked.connect(close_dialog)
            lineEdit_write_edit_sequence.setDisabled(True) if ssdna_comp_list[c_row][0] == 2 \
                else lineEdit_write_edit_sequence.setEnabled(True)
            run_write_edit = write_edit_seq_dialog.exec_()

            if run_write_edit == 1:
                edited_seq = lineEdit_write_edit_sequence.text()
                edited_amount = lineEdit_write_edit_amount.text()
                save_seq = save_edited_seq(c_row, edited_seq, edited_amount)

                if save_seq:
                    self.label_messages.setText('Sequence edited to successfully ✔')
                    validate_and_update_buttons(write_tab)

        def run_activate_run_advanced():
            if self.checkBox_run_advanced.isChecked():
                check_is_adv_data_1 = sum([1 for i in run_temper_data_g if i != '']) == 4
                check_is_adv_data_2 = sum([1 for i in run_time_data_g if i != '']) == 4

                if run_kt_list_g != {}:
                    if run_annealing_g and check_is_adv_data_1 and check_is_adv_data_2:
                        self.label_messages.setText('')
                        self.lineEdit_run_start_time.setDisabled(True)
                        self.lineEdit_run_n_dumps.setDisabled(True)
                        self.lineEdit_run_sim_end.setDisabled(True)

                    else:
                        self.lineEdit_run_start_time.setEnabled(True)
                        self.lineEdit_run_n_dumps.setEnabled(True)
                        self.lineEdit_run_sim_end.setEnabled(True)

                else:
                    self.checkBox_run_advanced.setChecked(False)
                    self.lineEdit_run_start_time.setEnabled(True)
                    self.lineEdit_run_n_dumps.setEnabled(True)
                    self.lineEdit_run_sim_end.setEnabled(True)
                    self.label_messages.setText('Advanced parameters not entered in advanced menu ✘')

            elif not self.checkBox_run_advanced.isChecked():
                self.lineEdit_run_start_time.setEnabled(True)
                self.lineEdit_run_n_dumps.setEnabled(True)
                self.lineEdit_run_sim_end.setEnabled(True)
                self.label_messages.setText('')

        def run_advanced():
            global source_file, advanced_bngl_path

            source_file = os.path.realpath(__file__).replace('\\', '/').rsplit('/', 1)[0] + \
                                       '/reference_files/reference_file.bngl'

            auto_cal_list = ['run_start_time', 'run_time_per_stage', 'run_dumps_per_stage',
                             'run_start_temp', 'run_d_temp', 'run_end_temp']

            def set_previous():
                lineEdit_run_start_time.setText(run_time_data_g[0])
                lineEdit_run_time_per_stage.setText(run_time_data_g[1])
                lineEdit_run_dumps_per_stage.setText(run_time_data_g[2])

                lineEdit_run_start_temp.setText(run_temper_data_g[0])
                lineEdit_run_d_temp.setText(run_temper_data_g[1])
                lineEdit_run_end_temp.setText(run_temper_data_g[2])

            def update_save_button():

                if checkBox_annealing.isChecked():
                    all_cells_check = sum([1 for i in kt_n_ann_cells.values() if i.text().endswith('.')]) == 0
                    annealing_data = [lineEdit_run_start_temp.text(), lineEdit_run_d_temp.text(),
                                      lineEdit_run_end_temp.text(),
                                      lineEdit_run_start_time.text(), lineEdit_run_time_per_stage.text(),
                                      lineEdit_run_dumps_per_stage.text()]

                    data_exists = sum([1 for i in annealing_data if i.strip() != '']) == 6

                    if data_exists and all_cells_check:
                        buttonBox_write_edit.setEnabled(True)

                    elif not data_exists or not all_cells_check:
                        buttonBox_write_edit.setDisabled(True)

                if not checkBox_annealing.isChecked():
                    kt_cells_check = sum([1 for i in kt_n_ann_cells.items() if i[0] not in auto_cal_list
                                          and i[1].text().endswith('.')]) == 0
                    if kt_cells_check:
                        buttonBox_write_edit.setEnabled(True)

                    elif not kt_cells_check:
                        buttonBox_write_edit.setDisabled(True)

            def set_k_values(f_path, call_from):
                lineEdit_run_advanced_browse_source.setText(f_path)

                kt_cells = {'Temp': [lineEdit_run_temp_p, lineEdit_run_temp_vdna],
                            'k1': [lineEdit_run_p_k1, lineEdit_run_vdna_k1],
                            'k2': [lineEdit_run_p_k2, lineEdit_run_vdna_k2],
                            'k3': [lineEdit_run_p_k3, lineEdit_run_vdna_k3],
                            'k4': [lineEdit_run_p_k4, lineEdit_run_vdna_k4],
                            'k5': [lineEdit_run_p_k5, lineEdit_run_vdna_k5],
                            'k6': [lineEdit_run_p_k6, lineEdit_run_vdna_k6],
                            'k7': [lineEdit_run_p_k7, lineEdit_run_vdna_k7],
                            'k8': [lineEdit_run_p_k8, lineEdit_run_vdna_k8],
                            'k9': [lineEdit_run_p_k9, lineEdit_run_vdna_k9],
                            'k10': [lineEdit_run_p_k10, lineEdit_run_vdna_k10],
                            'k11': [lineEdit_run_p_k11, lineEdit_run_vdna_k11],
                            'k12': [lineEdit_run_p_k12, lineEdit_run_vdna_k12]}

                def set_file_run_parameters(a):
                    k_data_r = get_k_values('system_files/reference_files/reference_file.bngl')

                    if a == 'get':
                        k_data_p = get_k_values(f_path) if run_kt_list_g == {} else run_kt_list_g
                        for ii in kt_cells.items():
                            if ii[0] in k_data_p:
                                ii[1][0].setText(k_data_p[ii[0]])
                            else:
                                ii[1][0].setText('')

                            if ii[0] in k_data_r:
                                ii[1][1].setText(k_data_r[ii[0]])
                            else:
                                ii[1][1].setText('')

                    elif a == 'set_d':
                        for ii in kt_cells.items():
                            if ii[0] in k_data_r:
                                ii[1][0].setText(k_data_r[ii[0]])
                            else:
                                ii[1][0].setText('')

                    elif a == 'set_o':
                        k_data_p = get_k_values(f_path)
                        for ii in kt_cells.items():
                            if ii[0] in k_data_p:
                                ii[1][0].setText(k_data_p[ii[0]])
                            else:
                                ii[1][0].setText('')

                set_file_run_parameters(call_from)

            def save_rnf_data():
                global run_kt_list_g, run_temper_data_g, run_time_data_g

                k_list_values = {'Temp': lineEdit_run_temp_p.text(),
                                 'k1': lineEdit_run_p_k1.text(), 'k2': lineEdit_run_p_k2.text(),
                                 'k3': lineEdit_run_p_k3.text(), 'k4': lineEdit_run_p_k4.text(),
                                 'k5': lineEdit_run_p_k5.text(), 'k6': lineEdit_run_p_k6.text(),
                                 'k7': lineEdit_run_p_k7.text(), 'k8': lineEdit_run_p_k8.text(),
                                 'k9': lineEdit_run_p_k9.text(), 'k10': lineEdit_run_p_k10.text(),
                                 'k11': lineEdit_run_p_k11.text(), 'k12': lineEdit_run_p_k12.text()}

                del_k = []
                for key, val in k_list_values.items():
                    if val == '':
                        del_k.append(key)

                for k in del_k:
                    del k_list_values[k]

                run_kt_list_g = k_list_values

                run_time_data_g = [lineEdit_run_start_time.text(), lineEdit_run_time_per_stage.text(),
                                   lineEdit_run_dumps_per_stage.text(), lineEdit_run_total_time.text()]

                run_temper_data_g = [lineEdit_run_start_temp.text(), lineEdit_run_d_temp.text(),
                                     lineEdit_run_end_temp.text(), lineEdit_run_n_stages.text()]

            def auto_cal():

                temp_data = [lineEdit_run_start_temp.text(), lineEdit_run_d_temp.text(),
                             lineEdit_run_end_temp.text()]
                time_data = [lineEdit_run_start_time.text(),
                             lineEdit_run_time_per_stage.text(), lineEdit_run_total_time.text()]

                float_temp_list = []
                float_time_list = []
                try:
                    float_temp_list_1 = [float(i) if i != '' else None for i in temp_data]
                    float_time_list_1 = [float(i) if i != '' else None for i in time_data]
                    float_temp_list = float_temp_list_1
                    float_time_list = float_time_list_1

                except:
                    pass

                try:
                    reverse_if_temp = sorted([float_temp_list[0], float_temp_list[2]])[::-1]
                    reverse_if_temp.insert(1, float_temp_list[1])

                    float_temp_list = reverse_if_temp

                except:
                    pass

                try:
                    n_stages = ceil(((float_temp_list[0] - float_temp_list[2]) / float_temp_list[1]) + 1)
                    lineEdit_run_n_stages.setText(str(n_stages))

                except:
                    lineEdit_run_n_stages.setText('NAN')

                try:
                    total_time = round(float_time_list[1] * int(lineEdit_run_n_stages.text()), 4)
                    lineEdit_run_total_time.setText(str(total_time))

                except:
                    lineEdit_run_total_time.setText('NAN')

                update_save_button()

            def validate_cell_values(call_from, int_or_float):
                global validated_float_g, validated_int_g

                current_item = kt_n_ann_cells[call_from].text()

                if int_or_float == 'float':
                    validated_float_g = current_item
                    validate_num(validate_float, '')

                    if current_item != validated_float_g:
                        kt_n_ann_cells[call_from].setText(validated_float_g)
                        validated_float_g = ''

                elif int_or_float == 'int':
                    validated_int_g = current_item
                    validate_num(validate_int, '')

                    if current_item != validated_int_g:
                        kt_n_ann_cells[call_from].setText(validated_int_g)
                        validated_int_g = ''

                if call_from in auto_cal_list:
                    auto_cal()
                else:
                    update_save_button()

            def activate_annealing(call_from):
                annealing_data = [lineEdit_run_start_time, lineEdit_run_time_per_stage,
                                  lineEdit_run_dumps_per_stage, lineEdit_run_end_temp,
                                  lineEdit_run_start_temp, lineEdit_run_d_temp]

                check_is_adv_data_1 = sum([1 for i in run_temper_data_g if i != '']) == 4
                check_is_adv_data_2 = sum([1 for i in run_time_data_g if i != '']) == 4

                if not call_from == 'u_clicked':
                    if run_annealing_g:
                        checkBox_annealing.setChecked(True)
                        for cell in annealing_data:
                            cell.setEnabled(True)
                        set_previous()

                    elif not run_annealing_g:
                        checkBox_annealing.setChecked(False)
                        for cell in annealing_data:
                            cell.setDisabled(True)
                        set_previous()

                if call_from == 'u_clicked':
                    if not checkBox_annealing.isChecked():
                        for cell in annealing_data:
                            cell.setDisabled(True)

                    elif checkBox_annealing.isChecked():
                        for cell in annealing_data:
                            cell.setEnabled(True)
                            set_previous()
                        if check_is_adv_data_1 and check_is_adv_data_2:
                            set_previous()

                update_save_button()

            def run_advanced_browse_source():
                global source_file

                win_heading_and_file_type = {run_advanced_browse: ['Browse source BNGL file', 'BNGL(*.bngl)']}

                path = str(os.path.dirname(str(read_s_loc(run_advanced_browse))))
                file_path, _ = QFileDialog.getOpenFileName(None, win_heading_and_file_type[run_advanced_browse][0],
                                                           path, win_heading_and_file_type[run_advanced_browse][1])

                if len(file_path) > 0:
                    validate_path_status = validate_path_link(file_path)

                    if validate_path_status[0]:

                        lineEdit_run_advanced_browse_source.setText(file_path)
                        write_s_loc(run_advanced_browse, file_path)
                        source_file = file_path
                        set_k_values(source_file, 'set_o')


            run_advanced_dialog = QDialog()
            run_advanced_dialog.resize(692, 810)
            run_advanced_dialog.setMaximumSize(QSize(700, 810))
            gridLayout_2 = QGridLayout(run_advanced_dialog)
            gridLayout_2.setObjectName(u"gridLayout_2")
            frame_2 = QFrame(run_advanced_dialog)
            frame_2.setObjectName(u"frame_2")
            frame_2.setFrameShape(QFrame.StyledPanel)
            frame_2.setFrameShadow(QFrame.Raised)
            gridLayout = QGridLayout(frame_2)
            gridLayout.setObjectName(u"gridLayout")
            verticalLayout = QVBoxLayout()
            verticalLayout.setObjectName(u"verticalLayout")
            gridLayout_visual_browse_source = QGridLayout()
            gridLayout_visual_browse_source.setObjectName(u"gridLayout_visual_browse_source")
            label_visual_browse_source_info = QLabel(frame_2)
            label_visual_browse_source_info.setObjectName(u"label_visual_browse_source_info")
            font = QFont()
            font.setPointSize(8)
            font.setItalic(True)
            label_visual_browse_source_info.setFont(font)
            label_visual_browse_source_info.setAlignment(Qt.AlignCenter)

            gridLayout_visual_browse_source.addWidget(label_visual_browse_source_info, 3, 0, 1, 1)

            lineEdit_run_advanced_browse_source = QLineEdit(frame_2)
            lineEdit_run_advanced_browse_source.setObjectName(u"lineEdit_run_advanced_browse_source")
            lineEdit_run_advanced_browse_source.setReadOnly(True)

            gridLayout_visual_browse_source.addWidget(lineEdit_run_advanced_browse_source, 2, 0, 1, 1)

            pushButton_run_advanced_browse_source = QPushButton(frame_2)
            pushButton_run_advanced_browse_source.setObjectName(u"pushButton_run_advanced_browse_source")

            gridLayout_visual_browse_source.addWidget(pushButton_run_advanced_browse_source, 2, 1, 1, 1)

            label_visual_browse_source = QLabel(frame_2)
            label_visual_browse_source.setObjectName(u"label_visual_browse_source")

            gridLayout_visual_browse_source.addWidget(label_visual_browse_source, 0, 0, 2, 1)

            frame_24 = QFrame(frame_2)
            frame_24.setObjectName(u"frame_24")
            frame_24.setFrameShape(QFrame.StyledPanel)
            frame_24.setFrameShadow(QFrame.Raised)

            gridLayout_visual_browse_source.addWidget(frame_24, 3, 1, 1, 1)

            frame_29 = QFrame(frame_2)
            frame_29.setObjectName(u"frame_29")
            frame_29.setFrameShape(QFrame.StyledPanel)
            frame_29.setFrameShadow(QFrame.Raised)

            gridLayout_visual_browse_source.addWidget(frame_29, 0, 1, 2, 1)

            verticalLayout.addLayout(gridLayout_visual_browse_source)

            frame_3 = QFrame(frame_2)
            frame_3.setObjectName(u"frame_3")
            frame_3.setFrameShape(QFrame.StyledPanel)
            frame_3.setFrameShadow(QFrame.Raised)

            verticalLayout.addWidget(frame_3)

            gridLayout_run_parameters_entry = QGridLayout()
            gridLayout_run_parameters_entry.setObjectName(u"gridLayout_run_parameters_entry")
            lineEdit_run_vdna_k5 = QLineEdit(frame_2)
            lineEdit_run_vdna_k5.setObjectName(u"lineEdit_run_vdna_k5")
            lineEdit_run_vdna_k5.setEnabled(False)
            sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(lineEdit_run_vdna_k5.sizePolicy().hasHeightForWidth())
            lineEdit_run_vdna_k5.setSizePolicy(sizePolicy)
            lineEdit_run_vdna_k5.setMinimumSize(QSize(100, 0))
            lineEdit_run_vdna_k5.setAlignment(Qt.AlignCenter)
            lineEdit_run_vdna_k5.setReadOnly(True)

            gridLayout_run_parameters_entry.addWidget(lineEdit_run_vdna_k5, 5, 4, 1, 1)

            frame_25 = QFrame(frame_2)
            frame_25.setObjectName(u"frame_25")
            frame_25.setFrameShape(QFrame.StyledPanel)
            frame_25.setFrameShadow(QFrame.Raised)

            gridLayout_run_parameters_entry.addWidget(frame_25, 15, 3, 1, 1)

            label_run_d_temp = QLabel(frame_2)
            label_run_d_temp.setObjectName(u"label_run_d_temp")
            label_run_d_temp.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(label_run_d_temp, 18, 2, 1, 1)

            lineEdit_run_p_k3 = QLineEdit(frame_2)
            lineEdit_run_p_k3.setObjectName(u"lineEdit_run_p_k3")
            sizePolicy.setHeightForWidth(lineEdit_run_p_k3.sizePolicy().hasHeightForWidth())
            lineEdit_run_p_k3.setSizePolicy(sizePolicy)
            lineEdit_run_p_k3.setMinimumSize(QSize(100, 0))
            lineEdit_run_p_k3.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(lineEdit_run_p_k3, 3, 2, 1, 1)

            label_run_k4 = QLabel(frame_2)
            label_run_k4.setObjectName(u"label_run_k4")
            label_run_k4.setMinimumSize(QSize(0, 25))
            label_run_k4.setMaximumSize(QSize(16777215, 16777215))
            label_run_k4.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(label_run_k4, 4, 0, 1, 1)

            lineEdit_run_vdna_k3 = QLineEdit(frame_2)
            lineEdit_run_vdna_k3.setObjectName(u"lineEdit_run_vdna_k3")
            lineEdit_run_vdna_k3.setEnabled(False)
            sizePolicy.setHeightForWidth(lineEdit_run_vdna_k3.sizePolicy().hasHeightForWidth())
            lineEdit_run_vdna_k3.setSizePolicy(sizePolicy)
            lineEdit_run_vdna_k3.setMinimumSize(QSize(100, 0))
            lineEdit_run_vdna_k3.setAlignment(Qt.AlignCenter)
            lineEdit_run_vdna_k3.setReadOnly(True)

            gridLayout_run_parameters_entry.addWidget(lineEdit_run_vdna_k3, 3, 4, 1, 1)

            label_run_present_values = QLabel(frame_2)
            label_run_present_values.setObjectName(u"label_run_present_values")
            label_run_present_values.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(label_run_present_values, 0, 2, 1, 1)

            lineEdit_run_vdna_k4 = QLineEdit(frame_2)
            lineEdit_run_vdna_k4.setObjectName(u"lineEdit_run_vdna_k4")
            lineEdit_run_vdna_k4.setEnabled(False)
            sizePolicy.setHeightForWidth(lineEdit_run_vdna_k4.sizePolicy().hasHeightForWidth())
            lineEdit_run_vdna_k4.setSizePolicy(sizePolicy)
            lineEdit_run_vdna_k4.setMinimumSize(QSize(100, 0))
            lineEdit_run_vdna_k4.setAlignment(Qt.AlignCenter)
            lineEdit_run_vdna_k4.setReadOnly(True)

            gridLayout_run_parameters_entry.addWidget(lineEdit_run_vdna_k4, 4, 4, 1, 1)

            lineEdit_run_temp_vdna = QLineEdit(frame_2)
            lineEdit_run_temp_vdna.setObjectName(u"lineEdit_run_temp_vdna")
            lineEdit_run_temp_vdna.setEnabled(False)
            sizePolicy.setHeightForWidth(lineEdit_run_temp_vdna.sizePolicy().hasHeightForWidth())
            lineEdit_run_temp_vdna.setSizePolicy(sizePolicy)
            lineEdit_run_temp_vdna.setMinimumSize(QSize(100, 0))
            lineEdit_run_temp_vdna.setAlignment(Qt.AlignCenter)
            lineEdit_run_temp_vdna.setReadOnly(True)

            gridLayout_run_parameters_entry.addWidget(lineEdit_run_temp_vdna, 15, 4, 1, 1)

            lineEdit_run_start_temp = QLineEdit(frame_2)
            lineEdit_run_start_temp.setObjectName(u"lineEdit_run_start_temp")
            sizePolicy.setHeightForWidth(lineEdit_run_start_temp.sizePolicy().hasHeightForWidth())
            lineEdit_run_start_temp.setSizePolicy(sizePolicy)
            lineEdit_run_start_temp.setMinimumSize(QSize(100, 0))
            lineEdit_run_start_temp.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(lineEdit_run_start_temp, 19, 0, 1, 1)

            frame_23 = QFrame(frame_2)
            frame_23.setObjectName(u"frame_23")
            sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            sizePolicy1.setHorizontalStretch(0)
            sizePolicy1.setVerticalStretch(0)
            sizePolicy1.setHeightForWidth(frame_23.sizePolicy().hasHeightForWidth())
            frame_23.setSizePolicy(sizePolicy1)
            frame_23.setMinimumSize(QSize(10, 0))
            frame_23.setFrameShape(QFrame.StyledPanel)
            frame_23.setFrameShadow(QFrame.Raised)

            gridLayout_run_parameters_entry.addWidget(frame_23, 15, 1, 1, 1)

            frame_33 = QFrame(frame_2)
            frame_33.setObjectName(u"frame_33")
            sizePolicy1.setHeightForWidth(frame_33.sizePolicy().hasHeightForWidth())
            frame_33.setSizePolicy(sizePolicy1)
            frame_33.setMinimumSize(QSize(10, 0))
            frame_33.setFrameShape(QFrame.StyledPanel)
            frame_33.setFrameShadow(QFrame.Raised)

            gridLayout_run_parameters_entry.addWidget(frame_33, 21, 1, 3, 1)

            label_run_start_time = QLabel(frame_2)
            label_run_start_time.setObjectName(u"label_run_start_time")
            label_run_start_time.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(label_run_start_time, 21, 0, 1, 1)

            frame_35 = QFrame(frame_2)
            frame_35.setObjectName(u"frame_35")
            sizePolicy1.setHeightForWidth(frame_35.sizePolicy().hasHeightForWidth())
            frame_35.setSizePolicy(sizePolicy1)
            frame_35.setMinimumSize(QSize(10, 0))
            frame_35.setFrameShape(QFrame.StyledPanel)
            frame_35.setFrameShadow(QFrame.Raised)

            gridLayout_run_parameters_entry.addWidget(frame_35, 21, 3, 3, 1)

            label_run_temp = QLabel(frame_2)
            label_run_temp.setObjectName(u"label_run_temp")
            label_run_temp.setMinimumSize(QSize(0, 25))
            label_run_temp.setMaximumSize(QSize(16777215, 16777215))
            label_run_temp.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(label_run_temp, 15, 0, 1, 1)

            label_run_start_temp = QLabel(frame_2)
            label_run_start_temp.setObjectName(u"label_run_start_temp")
            label_run_start_temp.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(label_run_start_temp, 18, 0, 1, 1)

            frame_8 = QFrame(frame_2)
            frame_8.setObjectName(u"frame_8")
            frame_8.setMinimumSize(QSize(0, 20))
            frame_8.setFrameShape(QFrame.StyledPanel)
            frame_8.setFrameShadow(QFrame.Raised)

            gridLayout_run_parameters_entry.addWidget(frame_8, 16, 0, 1, 8)

            label_run_kinetic_values = QLabel(frame_2)
            label_run_kinetic_values.setObjectName(u"label_run_kinetic_values")
            label_run_kinetic_values.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(label_run_kinetic_values, 0, 0, 1, 1)

            lineEdit_run_p_k2 = QLineEdit(frame_2)
            lineEdit_run_p_k2.setObjectName(u"lineEdit_run_p_k2")
            sizePolicy.setHeightForWidth(lineEdit_run_p_k2.sizePolicy().hasHeightForWidth())
            lineEdit_run_p_k2.setSizePolicy(sizePolicy)
            lineEdit_run_p_k2.setMinimumSize(QSize(100, 0))
            lineEdit_run_p_k2.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(lineEdit_run_p_k2, 2, 2, 1, 1)

            label_run_total_time = QLabel(frame_2)
            label_run_total_time.setObjectName(u"label_run_total_time")
            label_run_total_time.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(label_run_total_time, 21, 6, 1, 1)

            frame_27 = QFrame(frame_2)
            frame_27.setObjectName(u"frame_27")
            frame_27.setFrameShape(QFrame.StyledPanel)
            frame_27.setFrameShadow(QFrame.Raised)

            gridLayout_run_parameters_entry.addWidget(frame_27, 15, 6, 1, 2)

            frame_31 = QFrame(frame_2)
            frame_31.setObjectName(u"frame_31")
            frame_31.setFrameShape(QFrame.StyledPanel)
            frame_31.setFrameShadow(QFrame.Raised)

            gridLayout_run_parameters_entry.addWidget(frame_31, 17, 4, 1, 1)

            frame_26 = QFrame(frame_2)
            frame_26.setObjectName(u"frame_26")
            frame_26.setFrameShape(QFrame.StyledPanel)
            frame_26.setFrameShadow(QFrame.Raised)

            gridLayout_run_parameters_entry.addWidget(frame_26, 15, 5, 1, 1)

            label_run_k11 = QLabel(frame_2)
            label_run_k11.setObjectName(u"label_run_k11")
            label_run_k11.setMinimumSize(QSize(0, 25))
            label_run_k11.setMaximumSize(QSize(16777215, 16777215))
            label_run_k11.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(label_run_k11, 11, 0, 1, 1)

            lineEdit_run_vdna_k7 = QLineEdit(frame_2)
            lineEdit_run_vdna_k7.setObjectName(u"lineEdit_run_vdna_k7")
            lineEdit_run_vdna_k7.setEnabled(False)
            sizePolicy.setHeightForWidth(lineEdit_run_vdna_k7.sizePolicy().hasHeightForWidth())
            lineEdit_run_vdna_k7.setSizePolicy(sizePolicy)
            lineEdit_run_vdna_k7.setMinimumSize(QSize(100, 0))
            lineEdit_run_vdna_k7.setAlignment(Qt.AlignCenter)
            lineEdit_run_vdna_k7.setReadOnly(True)

            gridLayout_run_parameters_entry.addWidget(lineEdit_run_vdna_k7, 7, 4, 1, 1)

            lineEdit_run_n_stages = QLineEdit(frame_2)
            lineEdit_run_n_stages.setObjectName(u"lineEdit_run_n_stages")
            lineEdit_run_n_stages.setEnabled(False)
            sizePolicy.setHeightForWidth(lineEdit_run_n_stages.sizePolicy().hasHeightForWidth())
            lineEdit_run_n_stages.setSizePolicy(sizePolicy)
            lineEdit_run_n_stages.setMinimumSize(QSize(100, 0))
            lineEdit_run_n_stages.setAlignment(Qt.AlignCenter)
            lineEdit_run_n_stages.setReadOnly(True)

            gridLayout_run_parameters_entry.addWidget(lineEdit_run_n_stages, 19, 6, 1, 1)

            lineEdit_run_p_k11 = QLineEdit(frame_2)
            lineEdit_run_p_k11.setObjectName(u"lineEdit_run_p_k11")
            sizePolicy.setHeightForWidth(lineEdit_run_p_k11.sizePolicy().hasHeightForWidth())
            lineEdit_run_p_k11.setSizePolicy(sizePolicy)
            lineEdit_run_p_k11.setMinimumSize(QSize(100, 0))
            lineEdit_run_p_k11.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(lineEdit_run_p_k11, 11, 2, 1, 1)

            frame_5 = QFrame(frame_2)
            frame_5.setObjectName(u"frame_5")
            frame_5.setMinimumSize(QSize(0, 20))
            frame_5.setFrameShape(QFrame.StyledPanel)
            frame_5.setFrameShadow(QFrame.Raised)

            gridLayout_run_parameters_entry.addWidget(frame_5, 20, 0, 1, 8)

            lineEdit_run_p_k1 = QLineEdit(frame_2)
            lineEdit_run_p_k1.setObjectName(u"lineEdit_run_p_k1")
            sizePolicy.setHeightForWidth(lineEdit_run_p_k1.sizePolicy().hasHeightForWidth())
            lineEdit_run_p_k1.setSizePolicy(sizePolicy)
            lineEdit_run_p_k1.setMinimumSize(QSize(100, 0))
            lineEdit_run_p_k1.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(lineEdit_run_p_k1, 1, 2, 1, 1)

            pushButton_reset_to_originals = QPushButton(frame_2)
            pushButton_reset_to_originals.setObjectName(u"pushButton_reset_to_originals")

            gridLayout_run_parameters_entry.addWidget(pushButton_reset_to_originals, 7, 6, 1, 2)

            label_run_k7 = QLabel(frame_2)
            label_run_k7.setObjectName(u"label_run_k7")
            label_run_k7.setMinimumSize(QSize(0, 25))
            label_run_k7.setMaximumSize(QSize(16777215, 16777215))
            label_run_k7.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(label_run_k7, 7, 0, 1, 1)

            label_run_tempereture = QLabel(frame_2)
            label_run_tempereture.setObjectName(u"label_run_tempereture")
            label_run_tempereture.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(label_run_tempereture, 14, 0, 1, 1)

            lineEdit_run_p_k7 = QLineEdit(frame_2)
            lineEdit_run_p_k7.setObjectName(u"lineEdit_run_p_k7")
            sizePolicy.setHeightForWidth(lineEdit_run_p_k7.sizePolicy().hasHeightForWidth())
            lineEdit_run_p_k7.setSizePolicy(sizePolicy)
            lineEdit_run_p_k7.setMinimumSize(QSize(100, 0))
            lineEdit_run_p_k7.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(lineEdit_run_p_k7, 7, 2, 1, 1)

            frame_28 = QFrame(frame_2)
            frame_28.setObjectName(u"frame_28")
            sizePolicy1.setHeightForWidth(frame_28.sizePolicy().hasHeightForWidth())
            frame_28.setSizePolicy(sizePolicy1)
            frame_28.setMinimumSize(QSize(10, 0))
            frame_28.setFrameShape(QFrame.StyledPanel)
            frame_28.setFrameShadow(QFrame.Raised)

            gridLayout_run_parameters_entry.addWidget(frame_28, 14, 1, 1, 7)

            lineEdit_run_vdna_k2 = QLineEdit(frame_2)
            lineEdit_run_vdna_k2.setObjectName(u"lineEdit_run_vdna_k2")
            lineEdit_run_vdna_k2.setEnabled(False)
            sizePolicy.setHeightForWidth(lineEdit_run_vdna_k2.sizePolicy().hasHeightForWidth())
            lineEdit_run_vdna_k2.setSizePolicy(sizePolicy)
            lineEdit_run_vdna_k2.setMinimumSize(QSize(100, 0))
            lineEdit_run_vdna_k2.setAlignment(Qt.AlignCenter)
            lineEdit_run_vdna_k2.setReadOnly(True)

            gridLayout_run_parameters_entry.addWidget(lineEdit_run_vdna_k2, 2, 4, 1, 1)

            frame_19 = QFrame(frame_2)
            frame_19.setObjectName(u"frame_19")
            sizePolicy1.setHeightForWidth(frame_19.sizePolicy().hasHeightForWidth())
            frame_19.setSizePolicy(sizePolicy1)
            frame_19.setMinimumSize(QSize(10, 0))
            frame_19.setFrameShape(QFrame.StyledPanel)
            frame_19.setFrameShadow(QFrame.Raised)

            gridLayout_run_parameters_entry.addWidget(frame_19, 17, 3, 3, 1)

            lineEdit_run_p_k6 = QLineEdit(frame_2)
            lineEdit_run_p_k6.setObjectName(u"lineEdit_run_p_k6")
            sizePolicy.setHeightForWidth(lineEdit_run_p_k6.sizePolicy().hasHeightForWidth())
            lineEdit_run_p_k6.setSizePolicy(sizePolicy)
            lineEdit_run_p_k6.setMinimumSize(QSize(100, 0))
            lineEdit_run_p_k6.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(lineEdit_run_p_k6, 6, 2, 1, 1)

            lineEdit_run_total_time = QLineEdit(frame_2)
            lineEdit_run_total_time.setObjectName(u"lineEdit_run_total_time")
            lineEdit_run_total_time.setEnabled(False)
            sizePolicy.setHeightForWidth(lineEdit_run_total_time.sizePolicy().hasHeightForWidth())
            lineEdit_run_total_time.setSizePolicy(sizePolicy)
            lineEdit_run_total_time.setMinimumSize(QSize(100, 0))
            lineEdit_run_total_time.setAlignment(Qt.AlignCenter)
            lineEdit_run_total_time.setReadOnly(True)

            gridLayout_run_parameters_entry.addWidget(lineEdit_run_total_time, 22, 6, 1, 1)

            label_run_k10 = QLabel(frame_2)
            label_run_k10.setObjectName(u"label_run_k10")
            label_run_k10.setMinimumSize(QSize(0, 25))
            label_run_k10.setMaximumSize(QSize(16777215, 16777215))
            label_run_k10.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(label_run_k10, 10, 0, 1, 1)

            frame_37 = QFrame(frame_2)
            frame_37.setObjectName(u"frame_37")
            sizePolicy1.setHeightForWidth(frame_37.sizePolicy().hasHeightForWidth())
            frame_37.setSizePolicy(sizePolicy1)
            frame_37.setMinimumSize(QSize(10, 0))
            frame_37.setFrameShape(QFrame.StyledPanel)
            frame_37.setFrameShadow(QFrame.Raised)

            gridLayout_run_parameters_entry.addWidget(frame_37, 21, 5, 3, 1)

            lineEdit_run_vdna_k1 = QLineEdit(frame_2)
            lineEdit_run_vdna_k1.setObjectName(u"lineEdit_run_vdna_k1")
            lineEdit_run_vdna_k1.setEnabled(False)
            sizePolicy.setHeightForWidth(lineEdit_run_vdna_k1.sizePolicy().hasHeightForWidth())
            lineEdit_run_vdna_k1.setSizePolicy(sizePolicy)
            lineEdit_run_vdna_k1.setMinimumSize(QSize(100, 0))
            lineEdit_run_vdna_k1.setAlignment(Qt.AlignCenter)
            lineEdit_run_vdna_k1.setReadOnly(True)

            gridLayout_run_parameters_entry.addWidget(lineEdit_run_vdna_k1, 1, 4, 1, 1)

            label_run_end_temp = QLabel(frame_2)
            label_run_end_temp.setObjectName(u"label_run_end_temp")
            label_run_end_temp.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(label_run_end_temp, 18, 4, 1, 1)

            lineEdit_run_d_temp = QLineEdit(frame_2)
            lineEdit_run_d_temp.setObjectName(u"lineEdit_run_d_temp")
            sizePolicy.setHeightForWidth(lineEdit_run_d_temp.sizePolicy().hasHeightForWidth())
            lineEdit_run_d_temp.setSizePolicy(sizePolicy)
            lineEdit_run_d_temp.setMinimumSize(QSize(100, 0))
            lineEdit_run_d_temp.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(lineEdit_run_d_temp, 19, 2, 1, 1)

            pushButton_set_vdna_defaults = QPushButton(frame_2)
            pushButton_set_vdna_defaults.setObjectName(u"pushButton_set_vdna_defaults")

            gridLayout_run_parameters_entry.addWidget(pushButton_set_vdna_defaults, 6, 6, 1, 2)

            label_run_k6 = QLabel(frame_2)
            label_run_k6.setObjectName(u"label_run_k6")
            label_run_k6.setMinimumSize(QSize(0, 25))
            label_run_k6.setMaximumSize(QSize(16777215, 16777215))
            label_run_k6.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(label_run_k6, 6, 0, 1, 1)

            lineEdit_run_p_k8 = QLineEdit(frame_2)
            lineEdit_run_p_k8.setObjectName(u"lineEdit_run_p_k8")
            sizePolicy.setHeightForWidth(lineEdit_run_p_k8.sizePolicy().hasHeightForWidth())
            lineEdit_run_p_k8.setSizePolicy(sizePolicy)
            lineEdit_run_p_k8.setMinimumSize(QSize(100, 0))
            lineEdit_run_p_k8.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(lineEdit_run_p_k8, 8, 2, 1, 1)

            frame_17 = QFrame(frame_2)
            frame_17.setObjectName(u"frame_17")
            sizePolicy1.setHeightForWidth(frame_17.sizePolicy().hasHeightForWidth())
            frame_17.setSizePolicy(sizePolicy1)
            frame_17.setMinimumSize(QSize(10, 0))
            frame_17.setFrameShape(QFrame.StyledPanel)
            frame_17.setFrameShadow(QFrame.Raised)

            gridLayout_run_parameters_entry.addWidget(frame_17, 17, 5, 3, 1)

            lineEdit_run_end_temp = QLineEdit(frame_2)
            lineEdit_run_end_temp.setObjectName(u"lineEdit_run_end_temp")
            sizePolicy.setHeightForWidth(lineEdit_run_end_temp.sizePolicy().hasHeightForWidth())
            lineEdit_run_end_temp.setSizePolicy(sizePolicy)
            lineEdit_run_end_temp.setMinimumSize(QSize(100, 0))
            lineEdit_run_end_temp.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(lineEdit_run_end_temp, 19, 4, 1, 1)

            frame_14 = QFrame(frame_2)
            frame_14.setObjectName(u"frame_14")
            sizePolicy1.setHeightForWidth(frame_14.sizePolicy().hasHeightForWidth())
            frame_14.setSizePolicy(sizePolicy1)
            frame_14.setMinimumSize(QSize(10, 0))
            frame_14.setFrameShape(QFrame.StyledPanel)
            frame_14.setFrameShadow(QFrame.Raised)

            gridLayout_run_parameters_entry.addWidget(frame_14, 0, 6, 1, 2)

            frame_21 = QFrame(frame_2)
            frame_21.setObjectName(u"frame_21")
            sizePolicy1.setHeightForWidth(frame_21.sizePolicy().hasHeightForWidth())
            frame_21.setSizePolicy(sizePolicy1)
            frame_21.setMinimumSize(QSize(10, 0))
            frame_21.setFrameShape(QFrame.StyledPanel)
            frame_21.setFrameShadow(QFrame.Raised)

            gridLayout_run_parameters_entry.addWidget(frame_21, 17, 1, 3, 1)

            label_run_vdna_defaults = QLabel(frame_2)
            label_run_vdna_defaults.setObjectName(u"label_run_vdna_defaults")
            label_run_vdna_defaults.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(label_run_vdna_defaults, 0, 4, 1, 1)

            frame_32 = QFrame(frame_2)
            frame_32.setObjectName(u"frame_32")
            frame_32.setFrameShape(QFrame.StyledPanel)
            frame_32.setFrameShadow(QFrame.Raised)

            gridLayout_run_parameters_entry.addWidget(frame_32, 17, 6, 1, 1)

            label_run_k3 = QLabel(frame_2)
            label_run_k3.setObjectName(u"label_run_k3")
            label_run_k3.setMinimumSize(QSize(0, 25))
            label_run_k3.setMaximumSize(QSize(16777215, 16777215))
            label_run_k3.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(label_run_k3, 3, 0, 1, 1)

            lineEdit_run_p_k5 = QLineEdit(frame_2)
            lineEdit_run_p_k5.setObjectName(u"lineEdit_run_p_k5")
            sizePolicy.setHeightForWidth(lineEdit_run_p_k5.sizePolicy().hasHeightForWidth())
            lineEdit_run_p_k5.setSizePolicy(sizePolicy)
            lineEdit_run_p_k5.setMinimumSize(QSize(100, 0))
            lineEdit_run_p_k5.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(lineEdit_run_p_k5, 5, 2, 1, 1)

            lineEdit_run_vdna_k6 = QLineEdit(frame_2)
            lineEdit_run_vdna_k6.setObjectName(u"lineEdit_run_vdna_k6")
            lineEdit_run_vdna_k6.setEnabled(False)
            sizePolicy.setHeightForWidth(lineEdit_run_vdna_k6.sizePolicy().hasHeightForWidth())
            lineEdit_run_vdna_k6.setSizePolicy(sizePolicy)
            lineEdit_run_vdna_k6.setMinimumSize(QSize(100, 0))
            lineEdit_run_vdna_k6.setAlignment(Qt.AlignCenter)
            lineEdit_run_vdna_k6.setReadOnly(True)

            gridLayout_run_parameters_entry.addWidget(lineEdit_run_vdna_k6, 6, 4, 1, 1)

            label_run_k5 = QLabel(frame_2)
            label_run_k5.setObjectName(u"label_run_k5")
            label_run_k5.setMinimumSize(QSize(0, 25))
            label_run_k5.setMaximumSize(QSize(16777215, 16777215))
            label_run_k5.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(label_run_k5, 5, 0, 1, 1)

            lineEdit_run_vdna_k11 = QLineEdit(frame_2)
            lineEdit_run_vdna_k11.setObjectName(u"lineEdit_run_vdna_k11")
            lineEdit_run_vdna_k11.setEnabled(False)
            sizePolicy.setHeightForWidth(lineEdit_run_vdna_k11.sizePolicy().hasHeightForWidth())
            lineEdit_run_vdna_k11.setSizePolicy(sizePolicy)
            lineEdit_run_vdna_k11.setMinimumSize(QSize(100, 0))
            lineEdit_run_vdna_k11.setAlignment(Qt.AlignCenter)
            lineEdit_run_vdna_k11.setReadOnly(True)

            gridLayout_run_parameters_entry.addWidget(lineEdit_run_vdna_k11, 11, 4, 1, 1)

            lineEdit_run_vdna_k8 = QLineEdit(frame_2)
            lineEdit_run_vdna_k8.setObjectName(u"lineEdit_run_vdna_k8")
            lineEdit_run_vdna_k8.setEnabled(False)
            sizePolicy.setHeightForWidth(lineEdit_run_vdna_k8.sizePolicy().hasHeightForWidth())
            lineEdit_run_vdna_k8.setSizePolicy(sizePolicy)
            lineEdit_run_vdna_k8.setMinimumSize(QSize(100, 0))
            lineEdit_run_vdna_k8.setAlignment(Qt.AlignCenter)
            lineEdit_run_vdna_k8.setReadOnly(True)

            gridLayout_run_parameters_entry.addWidget(lineEdit_run_vdna_k8, 8, 4, 1, 1)

            lineEdit_run_p_k10 = QLineEdit(frame_2)
            lineEdit_run_p_k10.setObjectName(u"lineEdit_run_p_k10")
            sizePolicy.setHeightForWidth(lineEdit_run_p_k10.sizePolicy().hasHeightForWidth())
            lineEdit_run_p_k10.setSizePolicy(sizePolicy)
            lineEdit_run_p_k10.setMinimumSize(QSize(100, 0))
            lineEdit_run_p_k10.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(lineEdit_run_p_k10, 10, 2, 1, 1)

            label_run_dumps_per_stage = QLabel(frame_2)
            label_run_dumps_per_stage.setObjectName(u"label_run_dumps_per_stage")
            label_run_dumps_per_stage.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(label_run_dumps_per_stage, 21, 4, 1, 1)

            lineEdit_run_temp_p = QLineEdit(frame_2)
            lineEdit_run_temp_p.setObjectName(u"lineEdit_run_temp_p")
            sizePolicy.setHeightForWidth(lineEdit_run_temp_p.sizePolicy().hasHeightForWidth())
            lineEdit_run_temp_p.setSizePolicy(sizePolicy)
            lineEdit_run_temp_p.setMinimumSize(QSize(100, 0))
            lineEdit_run_temp_p.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(lineEdit_run_temp_p, 15, 2, 1, 1)

            lineEdit_run_p_k4 = QLineEdit(frame_2)
            lineEdit_run_p_k4.setObjectName(u"lineEdit_run_p_k4")
            sizePolicy.setHeightForWidth(lineEdit_run_p_k4.sizePolicy().hasHeightForWidth())
            lineEdit_run_p_k4.setSizePolicy(sizePolicy)
            lineEdit_run_p_k4.setMinimumSize(QSize(100, 0))
            lineEdit_run_p_k4.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(lineEdit_run_p_k4, 4, 2, 1, 1)

            lineEdit_run_vdna_k9 = QLineEdit(frame_2)
            lineEdit_run_vdna_k9.setObjectName(u"lineEdit_run_vdna_k9")
            lineEdit_run_vdna_k9.setEnabled(False)
            sizePolicy.setHeightForWidth(lineEdit_run_vdna_k9.sizePolicy().hasHeightForWidth())
            lineEdit_run_vdna_k9.setSizePolicy(sizePolicy)
            lineEdit_run_vdna_k9.setMinimumSize(QSize(100, 0))
            lineEdit_run_vdna_k9.setAlignment(Qt.AlignCenter)
            lineEdit_run_vdna_k9.setReadOnly(True)

            gridLayout_run_parameters_entry.addWidget(lineEdit_run_vdna_k9, 9, 4, 1, 1)

            label_run_k8 = QLabel(frame_2)
            label_run_k8.setObjectName(u"label_run_k8")
            label_run_k8.setMinimumSize(QSize(0, 25))
            label_run_k8.setMaximumSize(QSize(16777215, 16777215))
            label_run_k8.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(label_run_k8, 8, 0, 1, 1)

            lineEdit_run_vdna_k10 = QLineEdit(frame_2)
            lineEdit_run_vdna_k10.setObjectName(u"lineEdit_run_vdna_k10")
            lineEdit_run_vdna_k10.setEnabled(False)
            sizePolicy.setHeightForWidth(lineEdit_run_vdna_k10.sizePolicy().hasHeightForWidth())
            lineEdit_run_vdna_k10.setSizePolicy(sizePolicy)
            lineEdit_run_vdna_k10.setMinimumSize(QSize(100, 0))
            lineEdit_run_vdna_k10.setAlignment(Qt.AlignCenter)
            lineEdit_run_vdna_k10.setReadOnly(True)

            gridLayout_run_parameters_entry.addWidget(lineEdit_run_vdna_k10, 10, 4, 1, 1)

            lineEdit_run_start_time = QLineEdit(frame_2)
            lineEdit_run_start_time.setObjectName(u"lineEdit_run_start_time")
            sizePolicy.setHeightForWidth(lineEdit_run_start_time.sizePolicy().hasHeightForWidth())
            lineEdit_run_start_time.setSizePolicy(sizePolicy)
            lineEdit_run_start_time.setMinimumSize(QSize(100, 0))
            lineEdit_run_start_time.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(lineEdit_run_start_time, 22, 0, 2, 1)

            label_run_k1 = QLabel(frame_2)
            label_run_k1.setObjectName(u"label_run_k1")
            sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
            sizePolicy2.setHorizontalStretch(0)
            sizePolicy2.setVerticalStretch(0)
            sizePolicy2.setHeightForWidth(label_run_k1.sizePolicy().hasHeightForWidth())
            label_run_k1.setSizePolicy(sizePolicy2)
            label_run_k1.setMinimumSize(QSize(0, 25))
            label_run_k1.setMaximumSize(QSize(16777215, 16777215))
            label_run_k1.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(label_run_k1, 1, 0, 1, 1)

            label_run_k9 = QLabel(frame_2)
            label_run_k9.setObjectName(u"label_run_k9")
            label_run_k9.setMinimumSize(QSize(0, 25))
            label_run_k9.setMaximumSize(QSize(16777215, 16777215))
            label_run_k9.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(label_run_k9, 9, 0, 1, 1)

            frame_30 = QFrame(frame_2)
            frame_30.setObjectName(u"frame_30")
            frame_30.setMinimumSize(QSize(0, 20))
            frame_30.setFrameShape(QFrame.StyledPanel)
            frame_30.setFrameShadow(QFrame.Raised)

            gridLayout_run_parameters_entry.addWidget(frame_30, 17, 2, 1, 1)

            label_run_k2 = QLabel(frame_2)
            label_run_k2.setObjectName(u"label_run_k2")
            label_run_k2.setMinimumSize(QSize(0, 25))
            label_run_k2.setMaximumSize(QSize(16777215, 16777215))
            label_run_k2.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(label_run_k2, 2, 0, 1, 1)

            label_run_n_stages = QLabel(frame_2)
            label_run_n_stages.setObjectName(u"label_run_n_stages")
            label_run_n_stages.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(label_run_n_stages, 18, 6, 1, 1)

            lineEdit_run_dumps_per_stage = QLineEdit(frame_2)
            lineEdit_run_dumps_per_stage.setObjectName(u"lineEdit_run_dumps_per_stage")
            sizePolicy.setHeightForWidth(lineEdit_run_dumps_per_stage.sizePolicy().hasHeightForWidth())
            lineEdit_run_dumps_per_stage.setSizePolicy(sizePolicy)
            lineEdit_run_dumps_per_stage.setMinimumSize(QSize(100, 0))
            lineEdit_run_dumps_per_stage.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(lineEdit_run_dumps_per_stage, 22, 4, 1, 1)

            label_run_time_per_stage = QLabel(frame_2)
            label_run_time_per_stage.setObjectName(u"label_run_time_per_stage")
            label_run_time_per_stage.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(label_run_time_per_stage, 21, 2, 1, 1)

            lineEdit_run_p_k9 = QLineEdit(frame_2)
            lineEdit_run_p_k9.setObjectName(u"lineEdit_run_p_k9")
            sizePolicy.setHeightForWidth(lineEdit_run_p_k9.sizePolicy().hasHeightForWidth())
            lineEdit_run_p_k9.setSizePolicy(sizePolicy)
            lineEdit_run_p_k9.setMinimumSize(QSize(100, 0))
            lineEdit_run_p_k9.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(lineEdit_run_p_k9, 9, 2, 1, 1)

            lineEdit_run_time_per_stage = QLineEdit(frame_2)
            lineEdit_run_time_per_stage.setObjectName(u"lineEdit_run_time_per_stage")
            sizePolicy.setHeightForWidth(lineEdit_run_time_per_stage.sizePolicy().hasHeightForWidth())
            lineEdit_run_time_per_stage.setSizePolicy(sizePolicy)
            lineEdit_run_time_per_stage.setMinimumSize(QSize(100, 0))
            lineEdit_run_time_per_stage.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(lineEdit_run_time_per_stage, 22, 2, 1, 1)

            checkBox_annealing = QCheckBox(frame_2)
            checkBox_annealing.setObjectName(u"checkBox_annealing")
            sizePolicy.setHeightForWidth(checkBox_annealing.sizePolicy().hasHeightForWidth())
            checkBox_annealing.setSizePolicy(sizePolicy)
            checkBox_annealing.setMinimumSize(QSize(100, 0))
            font1 = QFont()
            font1.setBold(True)
            font1.setWeight(75)
            checkBox_annealing.setFont(font1)

            gridLayout_run_parameters_entry.addWidget(checkBox_annealing, 17, 0, 1, 1)

            frame_4 = QFrame(frame_2)
            frame_4.setObjectName(u"frame_4")
            frame_4.setMinimumSize(QSize(0, 20))
            frame_4.setFrameShape(QFrame.StyledPanel)
            frame_4.setFrameShadow(QFrame.Raised)

            gridLayout_run_parameters_entry.addWidget(frame_4, 13, 0, 1, 8)

            label_run_k12 = QLabel(frame_2)
            label_run_k12.setObjectName(u"label_run_k12")
            label_run_k12.setMinimumSize(QSize(0, 25))
            label_run_k12.setMaximumSize(QSize(16777215, 16777215))
            label_run_k12.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(label_run_k12, 12, 0, 1, 1)

            frame_15 = QFrame(frame_2)
            frame_15.setObjectName(u"frame_15")
            sizePolicy1.setHeightForWidth(frame_15.sizePolicy().hasHeightForWidth())
            frame_15.setSizePolicy(sizePolicy1)
            frame_15.setMinimumSize(QSize(10, 0))
            frame_15.setFrameShape(QFrame.StyledPanel)
            frame_15.setFrameShadow(QFrame.Raised)

            gridLayout_run_parameters_entry.addWidget(frame_15, 0, 1, 13, 1)

            frame_10 = QFrame(frame_2)
            frame_10.setObjectName(u"frame_10")
            sizePolicy1.setHeightForWidth(frame_10.sizePolicy().hasHeightForWidth())
            frame_10.setSizePolicy(sizePolicy1)
            frame_10.setMinimumSize(QSize(10, 0))
            frame_10.setFrameShape(QFrame.StyledPanel)
            frame_10.setFrameShadow(QFrame.Raised)

            gridLayout_run_parameters_entry.addWidget(frame_10, 0, 3, 13, 1)

            frame_12 = QFrame(frame_2)
            frame_12.setObjectName(u"frame_12")
            sizePolicy1.setHeightForWidth(frame_12.sizePolicy().hasHeightForWidth())
            frame_12.setSizePolicy(sizePolicy1)
            frame_12.setMinimumSize(QSize(10, 0))
            frame_12.setFrameShape(QFrame.StyledPanel)
            frame_12.setFrameShadow(QFrame.Raised)

            gridLayout_run_parameters_entry.addWidget(frame_12, 0, 5, 13, 1)

            lineEdit_run_p_k12 = QLineEdit(frame_2)
            lineEdit_run_p_k12.setObjectName(u"lineEdit_run_p_k12")
            sizePolicy.setHeightForWidth(lineEdit_run_p_k12.sizePolicy().hasHeightForWidth())
            lineEdit_run_p_k12.setSizePolicy(sizePolicy)
            lineEdit_run_p_k12.setMinimumSize(QSize(100, 0))
            lineEdit_run_p_k12.setAlignment(Qt.AlignCenter)

            gridLayout_run_parameters_entry.addWidget(lineEdit_run_p_k12, 12, 2, 1, 1)

            lineEdit_run_vdna_k12 = QLineEdit(frame_2)
            lineEdit_run_vdna_k12.setObjectName(u"lineEdit_run_vdna_k12")
            lineEdit_run_vdna_k12.setEnabled(False)
            sizePolicy.setHeightForWidth(lineEdit_run_vdna_k12.sizePolicy().hasHeightForWidth())
            lineEdit_run_vdna_k12.setSizePolicy(sizePolicy)
            lineEdit_run_vdna_k12.setMinimumSize(QSize(100, 0))
            lineEdit_run_vdna_k12.setAlignment(Qt.AlignCenter)
            lineEdit_run_vdna_k12.setReadOnly(True)

            gridLayout_run_parameters_entry.addWidget(lineEdit_run_vdna_k12, 12, 4, 1, 1)

            verticalLayout.addLayout(gridLayout_run_parameters_entry)

            frame = QFrame(frame_2)
            frame.setObjectName(u"frame")
            frame.setMinimumSize(QSize(0, 20))
            frame.setFrameShape(QFrame.StyledPanel)
            frame.setFrameShadow(QFrame.Raised)

            verticalLayout.addWidget(frame)

            horizontalLayout_save_cancel = QHBoxLayout()
            horizontalLayout_save_cancel.setObjectName(u"horizontalLayout_save_cancel")
            buttonBox_write_edit = QDialogButtonBox(frame_2)
            buttonBox_write_edit.setObjectName(u"buttonBox_write_edit")
            font2 = QFont()
            font2.setKerning(True)
            buttonBox_write_edit.setFont(font2)
            buttonBox_write_edit.setOrientation(Qt.Horizontal)
            buttonBox_write_edit.setStandardButtons(QDialogButtonBox.Save)

            horizontalLayout_save_cancel.addWidget(buttonBox_write_edit)

            pushButton_cancel = QPushButton(frame_2)
            pushButton_cancel.setObjectName(u"pushButton_cancel")

            horizontalLayout_save_cancel.addWidget(pushButton_cancel)

            verticalLayout.addLayout(horizontalLayout_save_cancel)

            gridLayout.addLayout(verticalLayout, 0, 0, 1, 1)

            gridLayout_2.addWidget(frame_2, 0, 0, 1, 1)


            def retranslateUi(Dialog):
                Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Advanced options", None))
                label_visual_browse_source_info.setText(
                    QCoreApplication.translate("Dialog", u"Acceptable file format ( .bngl )", None))
                pushButton_run_advanced_browse_source.setText(QCoreApplication.translate("Dialog", u"Browse", None))
                label_visual_browse_source.setText(QCoreApplication.translate("Dialog", u"Source BNGL file", None))
                label_run_d_temp.setText(QCoreApplication.translate("Dialog", u"\u0394 tempreture", None))
                label_run_k4.setText(QCoreApplication.translate("Dialog", u"k 4", None))
                label_run_present_values.setText(QCoreApplication.translate("Dialog", u"Present values", None))
                label_run_start_time.setText(QCoreApplication.translate("Dialog", u"Start time", None))
                label_run_temp.setText(QCoreApplication.translate("Dialog", u"Temp", None))
                label_run_start_temp.setText(QCoreApplication.translate("Dialog", u"Start tempreture", None))
                label_run_kinetic_values.setText(QCoreApplication.translate("Dialog", u"Kinetic values", None))
                label_run_total_time.setText(QCoreApplication.translate("Dialog", u"Total time", None))
                label_run_k11.setText(QCoreApplication.translate("Dialog", u"k 11", None))
                pushButton_reset_to_originals.setText(QCoreApplication.translate("Dialog", u"Reset to file values", None))
                label_run_k7.setText(QCoreApplication.translate("Dialog", u"k 7", None))
                label_run_tempereture.setText(QCoreApplication.translate("Dialog", u"Tempereture", None))
                label_run_k10.setText(QCoreApplication.translate("Dialog", u"k 10", None))
                label_run_end_temp.setText(QCoreApplication.translate("Dialog", u"End tempereture", None))
                pushButton_set_vdna_defaults.setText(QCoreApplication.translate("Dialog", u"Reset to VDNA default", None))
                label_run_k6.setText(QCoreApplication.translate("Dialog", u"k 6", None))
                label_run_vdna_defaults.setText(QCoreApplication.translate("Dialog", u"VDNA defaults", None))
                label_run_k3.setText(QCoreApplication.translate("Dialog", u"k 3", None))
                label_run_k5.setText(QCoreApplication.translate("Dialog", u"k 5", None))
                label_run_dumps_per_stage.setText(QCoreApplication.translate("Dialog", u"# dumps per stage", None))
                label_run_k8.setText(QCoreApplication.translate("Dialog", u"k 8", None))
                label_run_k1.setText(QCoreApplication.translate("Dialog", u"k 1", None))
                label_run_k9.setText(QCoreApplication.translate("Dialog", u"k 9", None))
                label_run_k2.setText(QCoreApplication.translate("Dialog", u"k 2", None))
                label_run_n_stages.setText(QCoreApplication.translate("Dialog", u"# stages", None))
                label_run_time_per_stage.setText(QCoreApplication.translate("Dialog", u"Time per stage", None))
                checkBox_annealing.setText(QCoreApplication.translate("Dialog", u"Annealing", None))
                label_run_k12.setText(QCoreApplication.translate("Dialog", u"k 12", None))
                pushButton_cancel.setText(QCoreApplication.translate("Dialog", u"Cancel", None))


            def close_dialog():
                run_advanced_dialog.reject()

            retranslateUi(run_advanced_dialog)
            buttonBox_write_edit.rejected.connect(run_advanced_dialog.reject)
            buttonBox_write_edit.accepted.connect(run_advanced_dialog.accept)

            QMetaObject.connectSlotsByName(run_advanced_dialog)

            kt_n_ann_cells = {'Temp_p': lineEdit_run_temp_p,
                              'k1_p': lineEdit_run_p_k1,
                              'k2_P': lineEdit_run_p_k2,
                              'k3_p': lineEdit_run_p_k3,
                              'k4_p': lineEdit_run_p_k4,
                              'k5_p': lineEdit_run_p_k5,
                              'k6_p': lineEdit_run_p_k6,
                              'k7_p': lineEdit_run_p_k7,
                              'k8_p': lineEdit_run_p_k8,
                              'k9_P': lineEdit_run_p_k9,
                              'k10_p': lineEdit_run_p_k10,
                              'k11_p': lineEdit_run_p_k11,
                              'k12_p': lineEdit_run_p_k12,
                              'run_start_time': lineEdit_run_start_time,
                              'run_time_per_stage': lineEdit_run_time_per_stage,
                              'run_dumps_per_stage': lineEdit_run_dumps_per_stage,
                              'run_start_temp': lineEdit_run_start_temp,
                              'run_d_temp': lineEdit_run_d_temp,
                              'run_end_temp': lineEdit_run_end_temp}

            set_k_values(source_file, 'get')
            lineEdit_run_n_stages.setText('NAN')
            lineEdit_run_total_time.setText('NAN')
            lineEdit_run_advanced_browse_source.setText(bngl_file_system_path)

            pushButton_run_advanced_browse_source.clicked.connect(run_advanced_browse_source)
            pushButton_set_vdna_defaults.clicked.connect(lambda: set_k_values(bngl_file_system_path, 'set_d'))
            pushButton_reset_to_originals.clicked.connect(lambda: set_k_values(source_file, 'set_o'))
            pushButton_cancel.clicked.connect(close_dialog)
            checkBox_annealing.clicked.connect(lambda: activate_annealing('u_clicked'))

            lineEdit_run_temp_p.textChanged.connect(lambda: validate_cell_values('Temp_p', 'float'))
            lineEdit_run_p_k1.textChanged.connect(lambda: validate_cell_values('k1_p', 'float'))
            lineEdit_run_p_k2.textChanged.connect(lambda: validate_cell_values('k2_P', 'float'))
            lineEdit_run_p_k3.textChanged.connect(lambda: validate_cell_values('k3_p', 'float'))
            lineEdit_run_p_k4.textChanged.connect(lambda: validate_cell_values('k4_p', 'float'))
            lineEdit_run_p_k5.textChanged.connect(lambda: validate_cell_values('k5_p', 'float'))
            lineEdit_run_p_k6.textChanged.connect(lambda: validate_cell_values('k6_p', 'float'))
            lineEdit_run_p_k7.textChanged.connect(lambda: validate_cell_values('k7_p', 'float'))
            lineEdit_run_p_k8.textChanged.connect(lambda: validate_cell_values('k8_p', 'float'))
            lineEdit_run_p_k9.textChanged.connect(lambda: validate_cell_values('k9_P', 'float'))
            lineEdit_run_p_k10.textChanged.connect(lambda: validate_cell_values('k10_p', 'float'))
            lineEdit_run_p_k11.textChanged.connect(lambda: validate_cell_values('k11_p', 'float'))
            lineEdit_run_p_k12.textChanged.connect(lambda: validate_cell_values('k12_p', 'float'))
            lineEdit_run_start_time.textChanged.connect(lambda: validate_cell_values('run_start_time', 'float'))
            lineEdit_run_time_per_stage.textChanged.connect(lambda: validate_cell_values('run_time_per_stage', 'float'))
            lineEdit_run_dumps_per_stage.textChanged.connect(lambda: validate_cell_values('run_dumps_per_stage', 'int'))
            lineEdit_run_start_temp.textChanged.connect(lambda: validate_cell_values('run_start_temp', 'float'))
            lineEdit_run_d_temp.textChanged.connect(lambda: validate_cell_values('run_d_temp', 'float'))
            lineEdit_run_end_temp.textChanged.connect(lambda: validate_cell_values('run_end_temp', 'float'))

            activate_annealing('')
            set_previous()

            run_run_advanced_dialog = run_advanced_dialog.exec_()

            if run_run_advanced_dialog == 1:
                global run_annealing_g, run_kt_g

                if checkBox_annealing.isChecked():
                    run_annealing_g = True
                elif not checkBox_annealing.isChecked():
                    run_annealing_g = False

                run_kt_g = True
                advanced_bngl_path = lineEdit_run_advanced_browse_source.text()
                save_rnf_data()
                self.checkBox_run_advanced.setChecked(True)
                run_activate_run_advanced()


        if MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(920, 763)
        font = QFont()
        font.setFamily(u"Segoe UI")
        font.setPointSize(9)
        MainWindow.setFont(font)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_main_title = QLabel(self.centralwidget)
        self.label_main_title.setObjectName(u"label_main_title")
        font1 = QFont()
        font1.setPointSize(15)
        font1.setBold(True)
        font1.setWeight(75)
        font1.setKerning(True)
        self.label_main_title.setFont(font1)
        self.label_main_title.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.label_main_title, 0, 0, 1, 1)

        self.frame_spacing_1 = QFrame(self.centralwidget)
        self.frame_spacing_1.setObjectName(u"frame_spacing_1")
        self.frame_spacing_1.setMinimumSize(QSize(0, 15))
        self.frame_spacing_1.setFrameShape(QFrame.StyledPanel)
        self.frame_spacing_1.setFrameShadow(QFrame.Raised)

        self.gridLayout.addWidget(self.frame_spacing_1, 2, 0, 1, 1)

        self.label_messages = QLabel(self.centralwidget)
        self.label_messages.setObjectName(u"label_messages")
        font2 = QFont()
        font2.setPointSize(9)
        font2.setBold(True)
        font2.setWeight(75)
        font2.setKerning(True)
        self.label_messages.setFont(font2)
        self.label_messages.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.label_messages, 5, 0, 1, 1)

        self.frame_spacing_2 = QFrame(self.centralwidget)
        self.frame_spacing_2.setObjectName(u"frame_spacing_2")
        self.frame_spacing_2.setMinimumSize(QSize(0, 15))
        self.frame_spacing_2.setFrameShape(QFrame.StyledPanel)
        self.frame_spacing_2.setFrameShadow(QFrame.Raised)

        self.gridLayout.addWidget(self.frame_spacing_2, 7, 0, 1, 1)

        self.main_tab = QTabWidget(self.centralwidget)
        self.main_tab.setObjectName(u"main_tab")
        font3 = QFont()
        font3.setBold(False)
        font3.setWeight(50)
        self.main_tab.setFont(font3)
        self.main_tab.setTabShape(QTabWidget.Triangular)
        self.tab_home = QWidget()
        self.tab_home.setObjectName(u"tab_home")
        self.gridLayout_3 = QGridLayout(self.tab_home)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.home_main_frame = QFrame(self.tab_home)
        self.home_main_frame.setObjectName(u"home_main_frame")
        self.home_main_frame.setEnabled(True)
        self.home_main_frame.setFrameShape(QFrame.StyledPanel)
        self.home_main_frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.home_main_frame)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(50, 50, 50, 50)
        self.textEdit_home_info = QTextEdit(self.home_main_frame)
        font_home = QFont()
        font_home.setPointSize(11)
        self.textEdit_home_info.setFont(font_home)
        self.textEdit_home_info.setObjectName(u"textEdit")
        self.textEdit_home_info.setFrameShape(QFrame.NoFrame)
        self.textEdit_home_info.setLineWidth(0)
        self.textEdit_home_info.setReadOnly(True)

        self.verticalLayout_4.addWidget(self.textEdit_home_info)


        self.gridLayout_3.addWidget(self.home_main_frame, 0, 0, 1, 1)

        self.main_tab.addTab(self.tab_home, "")
        self.tab_create_test_tube = QWidget()
        self.tab_create_test_tube.setObjectName(u"tab_create_test_tube")
        self.gridLayout_2 = QGridLayout(self.tab_create_test_tube)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.write_main_frame = QFrame(self.tab_create_test_tube)
        self.write_main_frame.setObjectName(u"write_main_frame")
        self.write_main_frame.setFrameShape(QFrame.StyledPanel)
        self.write_main_frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.write_main_frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(50, 50, 50, 50)
        self.verticalLayout_write_list_created = QVBoxLayout()
        self.verticalLayout_write_list_created.setObjectName(u"verticalLayout_write_list_created")
        self.label_write_list_created = QLabel(self.write_main_frame)
        self.label_write_list_created.setObjectName(u"label_write_list_created")

        self.verticalLayout_write_list_created.addWidget(self.label_write_list_created)

        self.listWidget_write_list_created = QListWidget(self.write_main_frame)
        self.listWidget_write_list_created.setObjectName(u"listWidget_write_list_created")
        self.listWidget_write_list_created.setMinimumSize(QSize(0, 0))

        font = QFont()
        font.setFamily("Lucida Console")
        self.listWidget_write_list_created.setFont(font)
        self.verticalLayout_write_list_created.addWidget(self.listWidget_write_list_created)


        self.verticalLayout.addLayout(self.verticalLayout_write_list_created)

        self.horizontalLayout_write_tool_buttons = QHBoxLayout()
        self.horizontalLayout_write_tool_buttons.setObjectName(u"horizontalLayout_write_tool_buttons")
        self.pushButton_write_edit = QPushButton(self.write_main_frame)
        self.pushButton_write_edit.setObjectName(u"pushButton_write_edit")

        self.horizontalLayout_write_tool_buttons.addWidget(self.pushButton_write_edit)

        self.frame_19 = QFrame(self.write_main_frame)
        self.frame_19.setObjectName(u"frame_19")
        self.frame_19.setFrameShape(QFrame.StyledPanel)
        self.frame_19.setFrameShadow(QFrame.Raised)

        self.horizontalLayout_write_tool_buttons.addWidget(self.frame_19)

        self.pushButton_write_delete = QPushButton(self.write_main_frame)
        self.pushButton_write_delete.setObjectName(u"pushButton_write_delete")

        self.horizontalLayout_write_tool_buttons.addWidget(self.pushButton_write_delete)

        self.frame_20 = QFrame(self.write_main_frame)
        self.frame_20.setObjectName(u"frame_20")
        self.frame_20.setFrameShape(QFrame.StyledPanel)
        self.frame_20.setFrameShadow(QFrame.Raised)

        self.horizontalLayout_write_tool_buttons.addWidget(self.frame_20)

        self.pushButton_write_reset_all = QPushButton(self.write_main_frame)
        self.pushButton_write_reset_all.setObjectName(u"pushButton_write_reset_all")

        self.horizontalLayout_write_tool_buttons.addWidget(self.pushButton_write_reset_all)


        self.verticalLayout.addLayout(self.horizontalLayout_write_tool_buttons)

        self.frame_35 = QFrame(self.write_main_frame)
        self.frame_35.setObjectName(u"frame_35")
        self.frame_35.setMinimumSize(QSize(0, 15))
        self.frame_35.setFrameShape(QFrame.StyledPanel)
        self.frame_35.setFrameShadow(QFrame.Raised)

        self.verticalLayout.addWidget(self.frame_35)

        self.gridLayout_write_sequence_entry = QGridLayout()
        self.gridLayout_write_sequence_entry.setObjectName(u"gridLayout_write_sequence_entry")
        self.pushButton_save = QPushButton(self.write_main_frame)
        self.pushButton_save.setObjectName(u"pushButton_save")
        font4 = QFont()
        font4.setPointSize(11)
        font4.setBold(True)
        font4.setWeight(75)
        self.pushButton_save.setFont(font4)

        self.gridLayout_write_sequence_entry.addWidget(self.pushButton_save, 7, 3, 1, 2)

        self.lineEdit_write_sequence = QLineEdit(self.write_main_frame)
        self.lineEdit_write_sequence.setObjectName(u"lineEdit_write_sequence")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_write_sequence.sizePolicy().hasHeightForWidth())
        self.lineEdit_write_sequence.setSizePolicy(sizePolicy)

        self.gridLayout_write_sequence_entry.addWidget(self.lineEdit_write_sequence, 1, 0, 1, 3)

        self.label_write_allowed_num = QLabel(self.write_main_frame)
        self.label_write_allowed_num.setObjectName(u"label_write_allowed_num")
        font5 = QFont()
        font5.setPointSize(8)
        font5.setBold(False)
        font5.setItalic(True)
        font5.setWeight(50)
        self.label_write_allowed_num.setFont(font5)
        self.label_write_allowed_num.setAlignment(Qt.AlignCenter)

        self.gridLayout_write_sequence_entry.addWidget(self.label_write_allowed_num, 2, 3, 1, 1)

        self.frame_4 = QFrame(self.write_main_frame)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setFrameShape(QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Raised)

        self.gridLayout_write_sequence_entry.addWidget(self.frame_4, 0, 4, 1, 1)

        self.lineEdit_custom_file_name = QLineEdit(self.write_main_frame)
        self.lineEdit_custom_file_name.setObjectName(u"lineEdit_custom_file_name")
        self.lineEdit_custom_file_name.setEnabled(False)
        self.lineEdit_custom_file_name.setReadOnly(True)

        self.gridLayout_write_sequence_entry.addWidget(self.lineEdit_custom_file_name, 5, 1, 1, 3)

        self.pushButton_save_species_browse = QPushButton(self.write_main_frame)
        self.pushButton_save_species_browse.setObjectName(u"pushButton_save_species_browse")

        self.gridLayout_write_sequence_entry.addWidget(self.pushButton_save_species_browse, 5, 4, 1, 1)

        self.label_write_allowed_char = QLabel(self.write_main_frame)
        self.label_write_allowed_char.setObjectName(u"label_write_allowed_char")
        self.label_write_allowed_char.setFont(font5)
        self.label_write_allowed_char.setAlignment(Qt.AlignCenter)

        self.gridLayout_write_sequence_entry.addWidget(self.label_write_allowed_char, 2, 1, 1, 1)

        self.frame_5 = QFrame(self.write_main_frame)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFrameShape(QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Raised)

        self.gridLayout_write_sequence_entry.addWidget(self.frame_5, 7, 1, 1, 1)

        self.frame_34 = QFrame(self.write_main_frame)
        self.frame_34.setObjectName(u"frame_34")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.frame_34.sizePolicy().hasHeightForWidth())
        self.frame_34.setSizePolicy(sizePolicy1)
        self.frame_34.setMinimumSize(QSize(0, 15))
        self.frame_34.setFrameShape(QFrame.StyledPanel)
        self.frame_34.setFrameShadow(QFrame.Raised)

        self.gridLayout_write_sequence_entry.addWidget(self.frame_34, 4, 0, 1, 5)

        self.frame_6 = QFrame(self.write_main_frame)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setFrameShape(QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QFrame.Raised)

        self.gridLayout_write_sequence_entry.addWidget(self.frame_6, 7, 2, 1, 1)

        self.checkBox_custom_file_name = QCheckBox(self.write_main_frame)
        self.checkBox_custom_file_name.setObjectName(u"checkBox_custom_file_name")

        self.gridLayout_write_sequence_entry.addWidget(self.checkBox_custom_file_name, 5, 0, 1, 1)

        self.frame_30 = QFrame(self.write_main_frame)
        self.frame_30.setObjectName(u"frame_30")
        self.frame_30.setFrameShape(QFrame.StyledPanel)
        self.frame_30.setFrameShadow(QFrame.Raised)

        self.gridLayout_write_sequence_entry.addWidget(self.frame_30, 2, 2, 1, 1)

        self.pushButton_write_add_sequence = QPushButton(self.write_main_frame)
        self.pushButton_write_add_sequence.setObjectName(u"pushButton_write_add_sequence")
        sizePolicy.setHeightForWidth(self.pushButton_write_add_sequence.sizePolicy().hasHeightForWidth())
        self.pushButton_write_add_sequence.setSizePolicy(sizePolicy)
        font6 = QFont()
        font6.setPointSize(9)
        font6.setBold(True)
        font6.setWeight(75)
        self.pushButton_write_add_sequence.setFont(font6)

        self.gridLayout_write_sequence_entry.addWidget(self.pushButton_write_add_sequence, 1, 4, 1, 1)

        self.label_write_amount = QLabel(self.write_main_frame)
        self.label_write_amount.setObjectName(u"label_write_amount")
        sizePolicy.setHeightForWidth(self.label_write_amount.sizePolicy().hasHeightForWidth())
        self.label_write_amount.setSizePolicy(sizePolicy)
        self.label_write_amount.setAlignment(Qt.AlignCenter)

        self.gridLayout_write_sequence_entry.addWidget(self.label_write_amount, 0, 3, 1, 1)

        self.frame_43 = QFrame(self.write_main_frame)
        self.frame_43.setObjectName(u"frame_43")
        sizePolicy1.setHeightForWidth(self.frame_43.sizePolicy().hasHeightForWidth())
        self.frame_43.setSizePolicy(sizePolicy1)
        self.frame_43.setMinimumSize(QSize(0, 5))
        self.frame_43.setFrameShape(QFrame.StyledPanel)
        self.frame_43.setFrameShadow(QFrame.Raised)

        self.gridLayout_write_sequence_entry.addWidget(self.frame_43, 6, 0, 1, 5)

        self.frame_8 = QFrame(self.write_main_frame)
        self.frame_8.setObjectName(u"frame_8")
        self.frame_8.setFrameShape(QFrame.StyledPanel)
        self.frame_8.setFrameShadow(QFrame.Raised)

        self.gridLayout_write_sequence_entry.addWidget(self.frame_8, 0, 2, 1, 1)

        self.lineEdit_write_amount = QLineEdit(self.write_main_frame)
        self.lineEdit_write_amount.setObjectName(u"lineEdit_write_amount")
        sizePolicy.setHeightForWidth(self.lineEdit_write_amount.sizePolicy().hasHeightForWidth())
        self.lineEdit_write_amount.setSizePolicy(sizePolicy)
        self.lineEdit_write_amount.setAlignment(Qt.AlignCenter)

        self.gridLayout_write_sequence_entry.addWidget(self.lineEdit_write_amount, 1, 3, 1, 1)

        self.pushButton_write_import_sequence = QPushButton(self.write_main_frame)
        self.pushButton_write_import_sequence.setObjectName(u"pushButton_write_import_sequence")
        sizePolicy.setHeightForWidth(self.pushButton_write_import_sequence.sizePolicy().hasHeightForWidth())
        self.pushButton_write_import_sequence.setSizePolicy(sizePolicy)
        font7 = QFont()
        font7.setPointSize(9)
        font7.setBold(False)
        font7.setWeight(50)
        self.pushButton_write_import_sequence.setFont(font7)

        self.gridLayout_write_sequence_entry.addWidget(self.pushButton_write_import_sequence, 2, 4, 1, 1)

        self.frame_32 = QFrame(self.write_main_frame)
        self.frame_32.setObjectName(u"frame_32")
        self.frame_32.setFrameShape(QFrame.StyledPanel)
        self.frame_32.setFrameShadow(QFrame.Raised)

        self.gridLayout_write_sequence_entry.addWidget(self.frame_32, 2, 0, 1, 1)

        self.frame_10 = QFrame(self.write_main_frame)
        self.frame_10.setObjectName(u"frame_10")
        self.frame_10.setFrameShape(QFrame.StyledPanel)
        self.frame_10.setFrameShadow(QFrame.Raised)

        self.gridLayout_write_sequence_entry.addWidget(self.frame_10, 7, 0, 1, 1)

        self.label_write_sequence = QLabel(self.write_main_frame)
        self.label_write_sequence.setObjectName(u"label_write_sequence")
        sizePolicy.setHeightForWidth(self.label_write_sequence.sizePolicy().hasHeightForWidth())
        self.label_write_sequence.setSizePolicy(sizePolicy)
        self.label_write_sequence.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.gridLayout_write_sequence_entry.addWidget(self.label_write_sequence, 0, 0, 1, 2)


        self.verticalLayout.addLayout(self.gridLayout_write_sequence_entry)


        self.gridLayout_2.addWidget(self.write_main_frame, 0, 0, 1, 1)

        self.main_tab.addTab(self.tab_create_test_tube, "")
        self.tab_run_experiment = QWidget()
        self.tab_run_experiment.setObjectName(u"tab_run_experiment")
        self.gridLayout_4 = QGridLayout(self.tab_run_experiment)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.run_main_frame = QFrame(self.tab_run_experiment)
        self.run_main_frame.setObjectName(u"run_main_frame")
        self.run_main_frame.setFrameShape(QFrame.StyledPanel)
        self.run_main_frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.run_main_frame)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(50, 50, 50, 50)
        self.gridLayout_run_browse_source = QGridLayout()
        self.gridLayout_run_browse_source.setObjectName(u"gridLayout_run_browse_source")
        self.label_run_browse_source_info = QLabel(self.run_main_frame)
        self.label_run_browse_source_info.setObjectName(u"label_run_browse_source_info")
        self.label_run_browse_source_info.setFont(font5)
        self.label_run_browse_source_info.setAlignment(Qt.AlignCenter)

        self.gridLayout_run_browse_source.addWidget(self.label_run_browse_source_info, 3, 0, 1, 1)

        self.pushButton_run_browse_source = QPushButton(self.run_main_frame)
        self.pushButton_run_browse_source.setObjectName(u"pushButton_run_browse_source")

        self.gridLayout_run_browse_source.addWidget(self.pushButton_run_browse_source, 2, 1, 1, 1)

        self.frame_16 = QFrame(self.run_main_frame)
        self.frame_16.setObjectName(u"frame_16")
        self.frame_16.setFrameShape(QFrame.StyledPanel)
        self.frame_16.setFrameShadow(QFrame.Raised)

        self.gridLayout_run_browse_source.addWidget(self.frame_16, 3, 1, 1, 1)

        self.lineEdit_run_browse_source = QLineEdit(self.run_main_frame)
        self.lineEdit_run_browse_source.setObjectName(u"lineEdit_run_browse_source")
        self.lineEdit_run_browse_source.setReadOnly(True)

        self.gridLayout_run_browse_source.addWidget(self.lineEdit_run_browse_source, 2, 0, 1, 1)

        self.label_run_browse_source = QLabel(self.run_main_frame)
        self.label_run_browse_source.setObjectName(u"label_run_browse_source")

        self.gridLayout_run_browse_source.addWidget(self.label_run_browse_source, 0, 0, 2, 1)

        self.frame_15 = QFrame(self.run_main_frame)
        self.frame_15.setObjectName(u"frame_15")
        self.frame_15.setFrameShape(QFrame.StyledPanel)
        self.frame_15.setFrameShadow(QFrame.Raised)

        self.gridLayout_run_browse_source.addWidget(self.frame_15, 0, 1, 2, 1)


        self.verticalLayout_3.addLayout(self.gridLayout_run_browse_source)

        self.frame = QFrame(self.run_main_frame)
        self.frame.setObjectName(u"frame")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy2)
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)

        self.verticalLayout_3.addWidget(self.frame)

        self.gridLayout_run_browse_source_des = QGridLayout()
        self.gridLayout_run_browse_source_des.setObjectName(u"gridLayout_run_browse_source_des")
        self.pushButton_run_browse_des = QPushButton(self.run_main_frame)
        self.pushButton_run_browse_des.setObjectName(u"pushButton_run_browse_des")

        self.gridLayout_run_browse_source_des.addWidget(self.pushButton_run_browse_des, 2, 1, 1, 1)

        self.label_run_browse_des_info = QLabel(self.run_main_frame)
        self.label_run_browse_des_info.setObjectName(u"label_run_browse_des_info")
        self.label_run_browse_des_info.setFont(font5)
        self.label_run_browse_des_info.setAlignment(Qt.AlignCenter)

        self.gridLayout_run_browse_source_des.addWidget(self.label_run_browse_des_info, 3, 0, 1, 1)

        self.lineEdit_run_browse_des = QLineEdit(self.run_main_frame)
        self.lineEdit_run_browse_des.setObjectName(u"lineEdit_run_browse_des")
        self.lineEdit_run_browse_des.setReadOnly(True)

        self.gridLayout_run_browse_source_des.addWidget(self.lineEdit_run_browse_des, 2, 0, 1, 1)

        self.frame_18 = QFrame(self.run_main_frame)
        self.frame_18.setObjectName(u"frame_18")
        self.frame_18.setFrameShape(QFrame.StyledPanel)
        self.frame_18.setFrameShadow(QFrame.Raised)

        self.gridLayout_run_browse_source_des.addWidget(self.frame_18, 3, 1, 1, 1)

        self.label_run_browse_des = QLabel(self.run_main_frame)
        self.label_run_browse_des.setObjectName(u"label_run_browse_des")

        self.gridLayout_run_browse_source_des.addWidget(self.label_run_browse_des, 0, 0, 2, 1)

        self.frame_17 = QFrame(self.run_main_frame)
        self.frame_17.setObjectName(u"frame_17")
        self.frame_17.setFrameShape(QFrame.StyledPanel)
        self.frame_17.setFrameShadow(QFrame.Raised)

        self.gridLayout_run_browse_source_des.addWidget(self.frame_17, 0, 1, 2, 1)


        self.verticalLayout_3.addLayout(self.gridLayout_run_browse_source_des)

        self.frame_2 = QFrame(self.run_main_frame)
        self.frame_2.setObjectName(u"frame_2")
        sizePolicy2.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy2)
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)

        self.verticalLayout_3.addWidget(self.frame_2)

        self.gridLayout_run_parameters_entry = QGridLayout()
        self.gridLayout_run_parameters_entry.setObjectName(u"gridLayout_run_parameters_entry")
        self.frame_47 = QFrame(self.run_main_frame)
        self.frame_47.setObjectName(u"frame_47")
        self.frame_47.setFrameShape(QFrame.StyledPanel)
        self.frame_47.setFrameShadow(QFrame.Raised)

        self.gridLayout_run_parameters_entry.addWidget(self.frame_47, 0, 6, 1, 1)

        self.pushButton_run_advanced = QPushButton(self.run_main_frame)
        self.pushButton_run_advanced.setObjectName(u"pushButton_run_advanced")

        self.gridLayout_run_parameters_entry.addWidget(self.pushButton_run_advanced, 1, 6, 1, 1)

        self.checkBox_run_advanced = QCheckBox(self.run_main_frame)
        self.checkBox_run_advanced.setObjectName(u"checkBox_run_advanced")

        self.gridLayout_run_parameters_entry.addWidget(self.checkBox_run_advanced, 1, 7, 1, 1)

        self.frame_48 = QFrame(self.run_main_frame)
        self.frame_48.setObjectName(u"frame_48")
        self.frame_48.setFrameShape(QFrame.StyledPanel)
        self.frame_48.setFrameShadow(QFrame.Raised)

        self.gridLayout_run_parameters_entry.addWidget(self.frame_48, 0, 7, 1, 1)

        self.lineEdit_run_n_dumps = QLineEdit(self.run_main_frame)
        self.lineEdit_run_n_dumps.setObjectName(u"lineEdit_run_n_dumps")
        sizePolicy.setHeightForWidth(self.lineEdit_run_n_dumps.sizePolicy().hasHeightForWidth())
        self.lineEdit_run_n_dumps.setSizePolicy(sizePolicy)
        self.lineEdit_run_n_dumps.setMinimumSize(QSize(100, 0))
        self.lineEdit_run_n_dumps.setAlignment(Qt.AlignCenter)

        self.gridLayout_run_parameters_entry.addWidget(self.lineEdit_run_n_dumps, 1, 2, 1, 1)

        self.frame_12 = QFrame(self.run_main_frame)
        self.frame_12.setObjectName(u"frame_12")
        self.frame_12.setFrameShape(QFrame.StyledPanel)
        self.frame_12.setFrameShadow(QFrame.Raised)

        self.gridLayout_run_parameters_entry.addWidget(self.frame_12, 0, 9, 1, 2)

        self.frame_11 = QFrame(self.run_main_frame)
        self.frame_11.setObjectName(u"frame_11")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.frame_11.sizePolicy().hasHeightForWidth())
        self.frame_11.setSizePolicy(sizePolicy3)
        self.frame_11.setMinimumSize(QSize(10, 0))
        self.frame_11.setFrameShape(QFrame.StyledPanel)
        self.frame_11.setFrameShadow(QFrame.Raised)

        self.gridLayout_run_parameters_entry.addWidget(self.frame_11, 0, 3, 2, 1)

        self.lineEdit_run_start_time = QLineEdit(self.run_main_frame)
        self.lineEdit_run_start_time.setObjectName(u"lineEdit_run_start_time")
        sizePolicy.setHeightForWidth(self.lineEdit_run_start_time.sizePolicy().hasHeightForWidth())
        self.lineEdit_run_start_time.setSizePolicy(sizePolicy)
        self.lineEdit_run_start_time.setMinimumSize(QSize(100, 0))
        self.lineEdit_run_start_time.setAlignment(Qt.AlignCenter)

        self.gridLayout_run_parameters_entry.addWidget(self.lineEdit_run_start_time, 1, 0, 1, 1)

        self.frame_24 = QFrame(self.run_main_frame)
        self.frame_24.setObjectName(u"frame_24")
        self.frame_24.setFrameShape(QFrame.StyledPanel)
        self.frame_24.setFrameShadow(QFrame.Raised)

        self.gridLayout_run_parameters_entry.addWidget(self.frame_24, 2, 0, 1, 11)

        self.label_run_start_time = QLabel(self.run_main_frame)
        self.label_run_start_time.setObjectName(u"label_run_start_time")
        self.label_run_start_time.setAlignment(Qt.AlignCenter)

        self.gridLayout_run_parameters_entry.addWidget(self.label_run_start_time, 0, 0, 1, 1)

        self.frame_25 = QFrame(self.run_main_frame)
        self.frame_25.setObjectName(u"frame_25")
        sizePolicy3.setHeightForWidth(self.frame_25.sizePolicy().hasHeightForWidth())
        self.frame_25.setSizePolicy(sizePolicy3)
        self.frame_25.setMinimumSize(QSize(50, 0))
        self.frame_25.setFrameShape(QFrame.StyledPanel)
        self.frame_25.setFrameShadow(QFrame.Raised)

        self.gridLayout_run_parameters_entry.addWidget(self.frame_25, 0, 5, 2, 1)

        self.label_run_n_dumps = QLabel(self.run_main_frame)
        self.label_run_n_dumps.setObjectName(u"label_run_n_dumps")
        self.label_run_n_dumps.setAlignment(Qt.AlignCenter)

        self.gridLayout_run_parameters_entry.addWidget(self.label_run_n_dumps, 0, 2, 1, 1)

        self.label_run_sim_end = QLabel(self.run_main_frame)
        self.label_run_sim_end.setObjectName(u"label_run_sim_end")
        self.label_run_sim_end.setAlignment(Qt.AlignCenter)

        self.gridLayout_run_parameters_entry.addWidget(self.label_run_sim_end, 0, 4, 1, 1)

        self.frame_9 = QFrame(self.run_main_frame)
        self.frame_9.setObjectName(u"frame_9")
        sizePolicy3.setHeightForWidth(self.frame_9.sizePolicy().hasHeightForWidth())
        self.frame_9.setSizePolicy(sizePolicy3)
        self.frame_9.setMinimumSize(QSize(10, 0))
        self.frame_9.setFrameShape(QFrame.StyledPanel)
        self.frame_9.setFrameShadow(QFrame.Raised)

        self.gridLayout_run_parameters_entry.addWidget(self.frame_9, 0, 1, 2, 1)

        self.pushButton_run_run = QPushButton(self.run_main_frame)
        self.pushButton_run_run.setObjectName(u"pushButton_run_run")
        sizePolicy4 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.pushButton_run_run.sizePolicy().hasHeightForWidth())
        self.pushButton_run_run.setSizePolicy(sizePolicy4)
        self.pushButton_run_run.setMinimumSize(QSize(150, 0))
        self.pushButton_run_run.setFont(font6)

        self.gridLayout_run_parameters_entry.addWidget(self.pushButton_run_run, 1, 9, 1, 2)

        self.lineEdit_run_sim_end = QLineEdit(self.run_main_frame)
        self.lineEdit_run_sim_end.setObjectName(u"lineEdit_run_sim_end")
        sizePolicy.setHeightForWidth(self.lineEdit_run_sim_end.sizePolicy().hasHeightForWidth())
        self.lineEdit_run_sim_end.setSizePolicy(sizePolicy)
        self.lineEdit_run_sim_end.setMinimumSize(QSize(100, 0))
        self.lineEdit_run_sim_end.setAlignment(Qt.AlignCenter)

        self.gridLayout_run_parameters_entry.addWidget(self.lineEdit_run_sim_end, 1, 4, 1, 1)

        self.frame_46 = QFrame(self.run_main_frame)
        self.frame_46.setObjectName(u"frame_46")
        sizePolicy3.setHeightForWidth(self.frame_46.sizePolicy().hasHeightForWidth())
        self.frame_46.setSizePolicy(sizePolicy3)
        self.frame_46.setMinimumSize(QSize(50, 0))
        self.frame_46.setFrameShape(QFrame.StyledPanel)
        self.frame_46.setFrameShadow(QFrame.Raised)

        self.gridLayout_run_parameters_entry.addWidget(self.frame_46, 0, 8, 2, 1)


        self.verticalLayout_3.addLayout(self.gridLayout_run_parameters_entry)

        self.frame_3 = QFrame(self.run_main_frame)
        self.frame_3.setObjectName(u"frame_3")
        sizePolicy1.setHeightForWidth(self.frame_3.sizePolicy().hasHeightForWidth())
        self.frame_3.setSizePolicy(sizePolicy1)
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)

        self.verticalLayout_3.addWidget(self.frame_3)


        self.gridLayout_4.addWidget(self.run_main_frame, 1, 0, 1, 1)

        self.main_tab.addTab(self.tab_run_experiment, "")
        self.tab_visualize_test_tube = QWidget()
        self.tab_visualize_test_tube.setObjectName(u"tab_visualize_test_tube")
        self.gridLayout_6 = QGridLayout(self.tab_visualize_test_tube)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.visualize_main_frame = QFrame(self.tab_visualize_test_tube)
        self.visualize_main_frame.setObjectName(u"visualize_main_frame")
        self.visualize_main_frame.setFrameShape(QFrame.StyledPanel)
        self.visualize_main_frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.visualize_main_frame)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(50, 50, 50, 50)
        self.gridLayout_visual_browse_source = QGridLayout()
        self.gridLayout_visual_browse_source.setObjectName(u"gridLayout_visual_browse_source")
        self.label_visual_browse_source_info = QLabel(self.visualize_main_frame)
        self.label_visual_browse_source_info.setObjectName(u"label_visual_browse_source_info")
        self.label_visual_browse_source_info.setFont(font5)
        self.label_visual_browse_source_info.setAlignment(Qt.AlignCenter)

        self.gridLayout_visual_browse_source.addWidget(self.label_visual_browse_source_info, 3, 0, 1, 1)

        self.lineEdit_visual_browse_source = QLineEdit(self.visualize_main_frame)
        self.lineEdit_visual_browse_source.setObjectName(u"lineEdit_visual_browse_source")

        self.gridLayout_visual_browse_source.addWidget(self.lineEdit_visual_browse_source, 2, 0, 1, 1)

        self.pushButton_visual_browse_source = QPushButton(self.visualize_main_frame)
        self.pushButton_visual_browse_source.setObjectName(u"pushButton_visual_browse_source")

        self.gridLayout_visual_browse_source.addWidget(self.pushButton_visual_browse_source, 2, 1, 1, 1)

        self.frame_23 = QFrame(self.visualize_main_frame)
        self.frame_23.setObjectName(u"frame_23")
        self.frame_23.setFrameShape(QFrame.StyledPanel)
        self.frame_23.setFrameShadow(QFrame.Raised)

        self.gridLayout_visual_browse_source.addWidget(self.frame_23, 3, 1, 1, 1)

        self.label_visual_browse_source = QLabel(self.visualize_main_frame)
        self.label_visual_browse_source.setObjectName(u"label_visual_browse_source")

        self.gridLayout_visual_browse_source.addWidget(self.label_visual_browse_source, 0, 0, 2, 1)

        self.frame_27 = QFrame(self.visualize_main_frame)
        self.frame_27.setObjectName(u"frame_27")
        self.frame_27.setFrameShape(QFrame.StyledPanel)
        self.frame_27.setFrameShadow(QFrame.Raised)

        self.gridLayout_visual_browse_source.addWidget(self.frame_27, 0, 1, 2, 1)


        self.verticalLayout_2.addLayout(self.gridLayout_visual_browse_source)

        self.frame_28 = QFrame(self.visualize_main_frame)
        self.frame_28.setObjectName(u"frame_28")
        sizePolicy1.setHeightForWidth(self.frame_28.sizePolicy().hasHeightForWidth())
        self.frame_28.setSizePolicy(sizePolicy1)
        self.frame_28.setMinimumSize(QSize(0, 15))
        self.frame_28.setFrameShape(QFrame.StyledPanel)
        self.frame_28.setFrameShadow(QFrame.Raised)

        self.verticalLayout_2.addWidget(self.frame_28)

        self.gridLayout_visual_history = QGridLayout()
        self.gridLayout_visual_history.setObjectName(u"gridLayout_visual_history")
        self.pushButton_visual_view_source = QPushButton(self.visualize_main_frame)
        self.pushButton_visual_view_source.setObjectName(u"pushButton_visual_view_source")
        sizePolicy.setHeightForWidth(self.pushButton_visual_view_source.sizePolicy().hasHeightForWidth())
        self.pushButton_visual_view_source.setSizePolicy(sizePolicy)
        self.pushButton_visual_view_source.setMinimumSize(QSize(200, 0))

        self.gridLayout_visual_history.addWidget(self.pushButton_visual_view_source, 6, 2, 1, 1)

        self.frame_39 = QFrame(self.visualize_main_frame)
        self.frame_39.setObjectName(u"frame_39")
        sizePolicy2.setHeightForWidth(self.frame_39.sizePolicy().hasHeightForWidth())
        self.frame_39.setSizePolicy(sizePolicy2)
        self.frame_39.setFrameShape(QFrame.StyledPanel)
        self.frame_39.setFrameShadow(QFrame.Raised)

        self.gridLayout_visual_history.addWidget(self.frame_39, 7, 2, 1, 1)

        self.pushButton_visual_delete = QPushButton(self.visualize_main_frame)
        self.pushButton_visual_delete.setObjectName(u"pushButton_visual_delete")
        self.pushButton_visual_delete.setMinimumSize(QSize(200, 0))

        self.gridLayout_visual_history.addWidget(self.pushButton_visual_delete, 8, 2, 1, 1)

        self.pushButton_visual_view_bngl = QPushButton(self.visualize_main_frame)
        self.pushButton_visual_view_bngl.setObjectName(u"pushButton_visual_view_bngl")
        sizePolicy.setHeightForWidth(self.pushButton_visual_view_bngl.sizePolicy().hasHeightForWidth())
        self.pushButton_visual_view_bngl.setSizePolicy(sizePolicy)
        self.pushButton_visual_view_bngl.setMinimumSize(QSize(200, 0))

        self.gridLayout_visual_history.addWidget(self.pushButton_visual_view_bngl, 4, 2, 1, 1)

        self.pushButton_visual_view_comp = QPushButton(self.visualize_main_frame)
        self.pushButton_visual_view_comp.setObjectName(u"pushButton_visual_view_comp")
        sizePolicy.setHeightForWidth(self.pushButton_visual_view_comp.sizePolicy().hasHeightForWidth())
        self.pushButton_visual_view_comp.setSizePolicy(sizePolicy)
        self.pushButton_visual_view_comp.setMinimumSize(QSize(200, 0))

        self.gridLayout_visual_history.addWidget(self.pushButton_visual_view_comp, 2, 2, 1, 1)

        self.label_visual_history = QLabel(self.visualize_main_frame)
        self.label_visual_history.setObjectName(u"label_visual_history")

        self.gridLayout_visual_history.addWidget(self.label_visual_history, 0, 0, 1, 1)

        self.frame_41 = QFrame(self.visualize_main_frame)
        self.frame_41.setObjectName(u"frame_41")
        sizePolicy2.setHeightForWidth(self.frame_41.sizePolicy().hasHeightForWidth())
        self.frame_41.setSizePolicy(sizePolicy2)
        self.frame_41.setFrameShape(QFrame.StyledPanel)
        self.frame_41.setFrameShadow(QFrame.Raised)

        self.gridLayout_visual_history.addWidget(self.frame_41, 9, 2, 1, 1)

        self.frame_42 = QFrame(self.visualize_main_frame)
        self.frame_42.setObjectName(u"frame_42")
        self.frame_42.setFrameShape(QFrame.StyledPanel)
        self.frame_42.setFrameShadow(QFrame.Raised)

        self.gridLayout_visual_history.addWidget(self.frame_42, 0, 2, 1, 1)

        self.frame_38 = QFrame(self.visualize_main_frame)
        self.frame_38.setObjectName(u"frame_38")
        sizePolicy2.setHeightForWidth(self.frame_38.sizePolicy().hasHeightForWidth())
        self.frame_38.setSizePolicy(sizePolicy2)
        self.frame_38.setFrameShape(QFrame.StyledPanel)
        self.frame_38.setFrameShadow(QFrame.Raised)

        self.gridLayout_visual_history.addWidget(self.frame_38, 5, 2, 1, 1)

        self.frame_29 = QFrame(self.visualize_main_frame)
        self.frame_29.setObjectName(u"frame_29")
        sizePolicy2.setHeightForWidth(self.frame_29.sizePolicy().hasHeightForWidth())
        self.frame_29.setSizePolicy(sizePolicy2)
        self.frame_29.setFrameShape(QFrame.StyledPanel)
        self.frame_29.setFrameShadow(QFrame.Raised)

        self.gridLayout_visual_history.addWidget(self.frame_29, 1, 2, 1, 1)

        self.frame_36 = QFrame(self.visualize_main_frame)
        self.frame_36.setObjectName(u"frame_36")
        sizePolicy2.setHeightForWidth(self.frame_36.sizePolicy().hasHeightForWidth())
        self.frame_36.setSizePolicy(sizePolicy2)
        self.frame_36.setFrameShape(QFrame.StyledPanel)
        self.frame_36.setFrameShadow(QFrame.Raised)

        self.gridLayout_visual_history.addWidget(self.frame_36, 3, 2, 1, 1)

        self.listWidget_visual_history_list = QListWidget(self.visualize_main_frame)
        self.listWidget_visual_history_list.setObjectName(u"listWidget_visual_history_list")
        sizePolicy5 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.listWidget_visual_history_list.sizePolicy().hasHeightForWidth())
        self.listWidget_visual_history_list.setSizePolicy(sizePolicy5)
        self.listWidget_visual_history_list.setMinimumSize(QSize(0, 0))

        self.gridLayout_visual_history.addWidget(self.listWidget_visual_history_list, 1, 0, 9, 1)

        self.frame_21 = QFrame(self.visualize_main_frame)
        self.frame_21.setObjectName(u"frame_21")
        self.frame_21.setMinimumSize(QSize(50, 0))
        self.frame_21.setFrameShape(QFrame.StyledPanel)
        self.frame_21.setFrameShadow(QFrame.Raised)

        self.gridLayout_visual_history.addWidget(self.frame_21, 0, 1, 10, 1)


        self.verticalLayout_2.addLayout(self.gridLayout_visual_history)

        self.frame_33 = QFrame(self.visualize_main_frame)
        self.frame_33.setObjectName(u"frame_33")
        sizePolicy1.setHeightForWidth(self.frame_33.sizePolicy().hasHeightForWidth())
        self.frame_33.setSizePolicy(sizePolicy1)
        self.frame_33.setMinimumSize(QSize(0, 15))
        self.frame_33.setFrameShape(QFrame.StyledPanel)
        self.frame_33.setFrameShadow(QFrame.Raised)

        self.verticalLayout_2.addWidget(self.frame_33)

        self.gridLayout_visual_browse_des = QGridLayout()
        self.gridLayout_visual_browse_des.setObjectName(u"gridLayout_visual_browse_des")
        self.pushButton_visual_browse_des = QPushButton(self.visualize_main_frame)
        self.pushButton_visual_browse_des.setObjectName(u"pushButton_visual_browse_des")

        self.gridLayout_visual_browse_des.addWidget(self.pushButton_visual_browse_des, 2, 1, 1, 1)

        self.label_visual_browse_des_info = QLabel(self.visualize_main_frame)
        self.label_visual_browse_des_info.setObjectName(u"label_visual_browse_des_info")
        self.label_visual_browse_des_info.setFont(font5)
        self.label_visual_browse_des_info.setAlignment(Qt.AlignCenter)

        self.gridLayout_visual_browse_des.addWidget(self.label_visual_browse_des_info, 3, 0, 1, 1)

        self.lineEdit_visual_browse_des = QLineEdit(self.visualize_main_frame)
        self.lineEdit_visual_browse_des.setObjectName(u"lineEdit_visual_browse_des")

        self.gridLayout_visual_browse_des.addWidget(self.lineEdit_visual_browse_des, 2, 0, 1, 1)

        self.frame_44 = QFrame(self.visualize_main_frame)
        self.frame_44.setObjectName(u"frame_44")
        self.frame_44.setFrameShape(QFrame.StyledPanel)
        self.frame_44.setFrameShadow(QFrame.Raised)

        self.gridLayout_visual_browse_des.addWidget(self.frame_44, 3, 1, 1, 1)

        self.label_visual_browse_des = QLabel(self.visualize_main_frame)
        self.label_visual_browse_des.setObjectName(u"label_visual_browse_des")

        self.gridLayout_visual_browse_des.addWidget(self.label_visual_browse_des, 0, 0, 2, 1)

        self.frame_45 = QFrame(self.visualize_main_frame)
        self.frame_45.setObjectName(u"frame_45")
        self.frame_45.setFrameShape(QFrame.StyledPanel)
        self.frame_45.setFrameShadow(QFrame.Raised)

        self.gridLayout_visual_browse_des.addWidget(self.frame_45, 0, 1, 2, 1)


        self.verticalLayout_2.addLayout(self.gridLayout_visual_browse_des)

        self.frame_37 = QFrame(self.visualize_main_frame)
        self.frame_37.setObjectName(u"frame_37")
        sizePolicy1.setHeightForWidth(self.frame_37.sizePolicy().hasHeightForWidth())
        self.frame_37.setSizePolicy(sizePolicy1)
        self.frame_37.setMinimumSize(QSize(0, 15))
        self.frame_37.setFrameShape(QFrame.StyledPanel)
        self.frame_37.setFrameShadow(QFrame.Raised)

        self.verticalLayout_2.addWidget(self.frame_37)

        self.gridLayout_visual_run = QGridLayout()
        self.gridLayout_visual_run.setObjectName(u"gridLayout_visual_run")
        self.pushButton_visual_advanced = QPushButton(self.visualize_main_frame)
        self.pushButton_visual_advanced.setObjectName(u"pushButton_visual_advanced")
        sizePolicy4.setHeightForWidth(self.pushButton_visual_advanced.sizePolicy().hasHeightForWidth())
        self.pushButton_visual_advanced.setSizePolicy(sizePolicy4)
        self.pushButton_visual_advanced.setFont(font7)

        self.gridLayout_visual_run.addWidget(self.pushButton_visual_advanced, 0, 2, 1, 1)

        self.checkBox_visual_advanced = QCheckBox(self.visualize_main_frame)
        self.checkBox_visual_advanced.setObjectName(u"checkBox_visual_advanced")
        sizePolicy6 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.checkBox_visual_advanced.sizePolicy().hasHeightForWidth())
        self.checkBox_visual_advanced.setSizePolicy(sizePolicy6)

        self.gridLayout_visual_run.addWidget(self.checkBox_visual_advanced, 0, 3, 1, 1)

        self.frame_40 = QFrame(self.visualize_main_frame)
        self.frame_40.setObjectName(u"frame_40")
        self.frame_40.setFrameShape(QFrame.StyledPanel)
        self.frame_40.setFrameShadow(QFrame.Raised)

        self.gridLayout_visual_run.addWidget(self.frame_40, 0, 4, 1, 2)

        self.pushButton_visual_visualize = QPushButton(self.visualize_main_frame)
        self.pushButton_visual_visualize.setObjectName(u"pushButton_visual_visualize")
        self.pushButton_visual_visualize.setFont(font4)

        self.gridLayout_visual_run.addWidget(self.pushButton_visual_visualize, 0, 7, 1, 1)


        self.verticalLayout_2.addLayout(self.gridLayout_visual_run)


        self.gridLayout_6.addWidget(self.visualize_main_frame, 0, 0, 1, 1)

        self.main_tab.addTab(self.tab_visualize_test_tube, "")

        self.gridLayout.addWidget(self.main_tab, 9, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.main_tab.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(MainWindow)

        """ all commands """

        # write bngl tab
        self.lineEdit_write_amount.setText('1')
        self.pushButton_save.clicked.connect(save_species)
        self.lineEdit_write_sequence.textChanged.connect(lambda: validate_char(write_the_seq))
        self.lineEdit_write_amount.textChanged.connect(lambda: validate_num(write_n_seq, write_tab))
        self.pushButton_save_species_browse.clicked.connect(lambda: browse_path(save_species_file, write_tab))
        self.pushButton_save_species_browse.setDisabled(True)
        self.pushButton_write_add_sequence.clicked.connect(add_sequence)
        self.pushButton_write_delete.clicked.connect(
            lambda: delete_created_sequences(self.listWidget_write_list_created.currentRow()))
        self.pushButton_write_reset_all.clicked.connect(reset_created_sequences_list)
        self.listWidget_write_list_created.itemClicked.connect(lambda: validate_and_update_buttons(write_tab))
        self.pushButton_write_reset_all.setDisabled(True)
        self.pushButton_write_delete.setDisabled(True)
        self.pushButton_write_edit.setDisabled(True)
        self.pushButton_write_add_sequence.setDisabled(True)
        self.pushButton_save.setDisabled(True)
        self.pushButton_write_import_sequence.clicked.connect(lambda: import_sequences(import_seq, write_tab))
        self.pushButton_write_edit.clicked.connect(lambda: edit_seq(self.listWidget_write_list_created.currentRow()))
        self.checkBox_custom_file_name.clicked.connect(save_species_dir)

        # run bngl
        self.lineEdit_run_start_time.setText('0')
        self.lineEdit_run_n_dumps.setText('10')
        self.lineEdit_run_sim_end.setText('1')
        self.pushButton_run_browse_source.clicked.connect(lambda: browse_path(run_b_source, run_tab))
        self.pushButton_run_browse_des.clicked.connect(lambda: browse_path(run_b_des, run_tab))
        self.pushButton_run_run.setDisabled(True)
        self.lineEdit_run_start_time.textChanged.connect(lambda: validate_num(run_start_time, run_tab))
        self.lineEdit_run_n_dumps.textChanged.connect(lambda: validate_num(run_n_dumps, run_tab))
        self.lineEdit_run_sim_end.textChanged.connect(lambda: validate_num(run_sim_end, run_tab))
        self.lineEdit_run_browse_source.textChanged.connect(lambda: on_edit_source_path(run_b_source, run_tab))
        self.lineEdit_run_browse_des.textChanged.connect(lambda: on_edit_des_dir(run_b_des, run_tab))
        self.pushButton_run_run.clicked.connect(run_bngl)
        self.pushButton_run_advanced.clicked.connect(run_advanced)
        self.checkBox_run_advanced.clicked.connect(run_activate_run_advanced)

        # visual bngl
        self.pushButton_visual_visualize.setDisabled(True)
        self.pushButton_visual_view_comp.setDisabled(True)
        self.pushButton_visual_view_source.setDisabled(True)
        self.pushButton_visual_view_bngl.setDisabled(True)
        self.pushButton_visual_delete.setDisabled(True)
        self.pushButton_visual_visualize.clicked.connect(lambda: run_visualisation(''))
        self.pushButton_visual_view_comp.clicked.connect(lambda: pop_view('.html', 'html'))
        self.pushButton_visual_view_source.clicked.connect(lambda: pop_view('.species', 's_sp'))
        self.pushButton_visual_view_bngl.clicked.connect(lambda: pop_view('.species', 'r_sp'))
        self.pushButton_visual_delete.clicked.connect(delete_folder)
        self.pushButton_visual_browse_source.clicked.connect(lambda: browse_path(visual_b_source, visual_tab))
        self.pushButton_visual_browse_des.clicked.connect(lambda: browse_path(visual_b_des, visual_tab))
        self.lineEdit_visual_browse_source.textChanged.connect(lambda: on_edit_source_path(visual_b_source, visual_tab))
        self.lineEdit_visual_browse_des.textChanged.connect(lambda: validate_and_update_buttons(visual_tab))
        self.listWidget_visual_history_list.itemClicked.connect(lambda: validate_and_update_buttons(visual_tab))
        self.lineEdit_visual_browse_des.textChanged.connect(lambda: on_edit_des_dir(visual_b_des, visual_tab))
        self.pushButton_visual_advanced.clicked.connect(advanced_options)

        def set_home_page():
            home_info_file_dir = os.path.realpath(__file__).replace('\\', '/').rsplit('/', 1)[0] + \
                                 '/home_page/home_info.txt'

            def get_home_info(f_p):
                with open(f_p, 'r') as f:
                    l = f.readlines()
                f.close()
                return l

            home_info_list = ''.join(get_home_info(home_info_file_dir))
            self.textEdit_home_info.setText(home_info_list)

        def restore_previous_session():
            all_source_cells = [[run_b_source, self.lineEdit_run_browse_source],
                                [visual_b_source, self.lineEdit_visual_browse_source]]

            all_des_cells = [[run_b_des, self.lineEdit_run_browse_des],
                             [visual_b_des, self.lineEdit_visual_browse_des]]

            for s_cells in all_source_cells:
                file_link = read_s_loc(s_cells[0])
                if os.path.isfile(file_link):
                    s_cells[1].setText(file_link)

            for des_cells in all_des_cells:
                dir_link = read_s_loc(des_cells[0])
                if os.path.isdir(dir_link):
                    des_cells[1].setText(dir_link)

        def set_browser():
            currect_browser_location = read_s_loc(web_browser_loc)

            if os.path.isfile(currect_browser_location):
                if not currect_browser_location.endswith('chrome.exe'):
                    consent = get_user_consent('web_browser_get', ['', ''])

                    if consent != None:
                        if consent == 16384:
                            b_loc = browse_path(web_browser_loc, '')
                            if b_loc != None:
                                write_s_loc(web_browser_loc, b_loc)
                                self.label_messages.setText('Program ready to run!')

            elif not os.path.isfile(currect_browser_location):
                consent = get_user_consent('web_browser_get', ['', ''])

                if consent != None:
                    if consent == 16384:
                        b_loc = browse_path(web_browser_loc, '')
                        if b_loc != None:
                            write_s_loc(web_browser_loc, b_loc)
                            self.label_messages.setText('Program ready to run!')

        set_home_page()
        set_browser()
        restore_previous_session()

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"VDNA Lab", None))
        self.label_main_title.setText(QCoreApplication.translate("MainWindow", u"Virtual DNA Lab", None))
        self.label_messages.setText("")
        self.textEdit_home_info.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt;\">Information file missing!</span></p></body></html>", None))
        self.main_tab.setTabText(self.main_tab.indexOf(self.tab_home), QCoreApplication.translate("MainWindow", u"Home", None))
        self.label_write_list_created.setText(QCoreApplication.translate("MainWindow", u"List of ssDNA to be created", None))
        self.pushButton_write_edit.setText(QCoreApplication.translate("MainWindow", u"Edit", None))
        self.pushButton_write_delete.setText(QCoreApplication.translate("MainWindow", u"Delete", None))
        self.pushButton_write_reset_all.setText(QCoreApplication.translate("MainWindow", u"Reset all", None))
        self.pushButton_save.setText(QCoreApplication.translate("MainWindow", u"Submit", None))
        self.label_write_allowed_num.setText(QCoreApplication.translate("MainWindow", u"Numericals only", None))
        self.pushButton_save_species_browse.setText(QCoreApplication.translate("MainWindow", u"Browse", None))
        self.label_write_allowed_char.setText(QCoreApplication.translate("MainWindow", u"Allowed characters (A, T, C, G)", None))
        self.checkBox_custom_file_name.setText(QCoreApplication.translate("MainWindow", u"Save as (.species) file", None))
        self.pushButton_write_add_sequence.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.label_write_amount.setText(QCoreApplication.translate("MainWindow", u"Amount", None))
        self.pushButton_write_import_sequence.setText(QCoreApplication.translate("MainWindow", u"Import from Species file", None))
        self.label_write_sequence.setText(QCoreApplication.translate("MainWindow", u"Desired ssDNA sequence (introduced in 5' to 3' order)", None))
        self.main_tab.setTabText(self.main_tab.indexOf(self.tab_create_test_tube), QCoreApplication.translate("MainWindow", u"Create Test Tube", None))
        self.label_run_browse_source_info.setText(QCoreApplication.translate("MainWindow", u"Only VDNA Lab generated (.species) file compatible", None))
        self.pushButton_run_browse_source.setText(QCoreApplication.translate("MainWindow", u"Browse", None))
        self.label_run_browse_source.setText(QCoreApplication.translate("MainWindow", u"Test tube", None))
        self.pushButton_run_browse_des.setText(QCoreApplication.translate("MainWindow", u"Browse", None))
        self.label_run_browse_des_info.setText(QCoreApplication.translate("MainWindow", u"Dump file(s) willl be saved to this directory", None))
        self.label_run_browse_des.setText(QCoreApplication.translate("MainWindow", u"Save simulation outputs directory", None))
        self.pushButton_run_advanced.setText(QCoreApplication.translate("MainWindow", u"Advanced", None))
        self.checkBox_run_advanced.setText("")
        self.label_run_start_time.setText(QCoreApplication.translate("MainWindow", u"Start time", None))
        self.label_run_n_dumps.setText(QCoreApplication.translate("MainWindow", u"Number of dumps", None))
        self.label_run_sim_end.setText(QCoreApplication.translate("MainWindow", u"Sim. end", None))
        self.pushButton_run_run.setText(QCoreApplication.translate("MainWindow", u"Run", None))
        self.main_tab.setTabText(self.main_tab.indexOf(self.tab_run_experiment), QCoreApplication.translate("MainWindow", u"Run Experiment", None))
        self.label_visual_browse_source_info.setText(QCoreApplication.translate("MainWindow", u"Acceptable file formats ( .species, .0 )", None))
        self.pushButton_visual_browse_source.setText(QCoreApplication.translate("MainWindow", u"Browse", None))
        self.label_visual_browse_source.setText(QCoreApplication.translate("MainWindow", u"Source file", None))
        self.pushButton_visual_view_source.setText(QCoreApplication.translate("MainWindow", u"View source", None))
        self.pushButton_visual_delete.setText(QCoreApplication.translate("MainWindow", u"Delete", None))
        self.pushButton_visual_view_bngl.setText(QCoreApplication.translate("MainWindow", u"View BNGL", None))
        self.pushButton_visual_view_comp.setText(QCoreApplication.translate("MainWindow", u"View complexes", None))
        self.label_visual_history.setText(QCoreApplication.translate("MainWindow", u"History", None))
        self.pushButton_visual_browse_des.setText(QCoreApplication.translate("MainWindow", u"Browse", None))
        self.label_visual_browse_des_info.setText(QCoreApplication.translate("MainWindow", u"Analysis output files willl be saved to this directory", None))
        self.label_visual_browse_des.setText(QCoreApplication.translate("MainWindow", u"Save analysis outputs directory", None))
        self.pushButton_visual_advanced.setText(QCoreApplication.translate("MainWindow", u"Advanced", None))
        self.checkBox_visual_advanced.setText("")
        self.pushButton_visual_visualize.setText(QCoreApplication.translate("MainWindow", u"Run visualization", None))
        self.main_tab.setTabText(self.main_tab.indexOf(self.tab_visualize_test_tube), QCoreApplication.translate("MainWindow", u"Visualize Test Tube", None))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
