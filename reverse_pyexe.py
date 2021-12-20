# -*- coding: utf-8 -*-
# @Time : 2021/12/16 16:21
# @Author : ordar
# @Project : reverse_pyexe
# @File : reverse_pyexe.py
# @Python: 3.7.5
import sys
import os
import threading
import multiprocessing
from pyinstxtractor import reverse_main
from hextool import HexTool


# 定义目录和文件
# root_path = os.getcwd()
root_path = os.path.split(os.path.abspath(sys.argv[0]))[0]
exe_file_path = sys.argv[1]
exe_file = os.path.basename(exe_file_path)  # "xxx.exe"
# exe_file_realpath = os.path.join(os.getcwd(), exe_file)     # exe文件绝对路径
exe_filename = os.path.basename(os.path.splitext(exe_file_path)[0])  # "xxx"
ext = os.path.splitext(exe_file_path)[-1]  # ".exe"
extracted_dir = exe_file + "_extracted"  # 逆向文件释放目录
extracted_package_dir = os.path.join(extracted_dir, "PYZ-00.pyz_extracted")  # 逆向依赖包文件释放目录
struct_file_path = os.path.join(extracted_dir, "struct")  # struct文件路径
# struct_file_path = os.path.join(root_path, struct_file_path)    # struct文件 绝对路径
key_file_path = os.path.join(extracted_dir, "pyimod00_crypto_key")  # 秘钥存放文件

out_dir = exe_file + "_out"  # 输出转换结果目录

# print(root_path, exe_file, main_file, ext, extracted_dir, extracted_package_dir, struct_file_path, main_file_path, out_dir)


def get_main_file():
    files = os.listdir(extracted_dir)
    for af in files:
        if af.endswith(".exe.manifest") and " " not in af:
            return str(af).replace(".exe.manifest", "")


def make_exe_package_files():
    #### 转换解密文件
    ht = HexTool(struct_file_path)
    # 转换入口文件
    out_pyc_files.append(ht.make_main_pyc(main_file_path))

    # 转换依赖包文件
    package_files = os.listdir(extracted_package_dir)
    # print(package_files)
    for file in package_files:
        # 过滤依赖文件,这里简单过滤
        if file.endswith(".pyc") and len(file.split(".")) == 2 and not file.startswith("_"):
            # if file.endswith(".pyc"):
            file_path = os.path.join(extracted_package_dir, file)
            ht.make_package_pyc(file_path)
            out_pyc_files.append(file_path)

    # print(len(out_pyc_files),out_pyc_files)

    #### 逆向还原文件，然后输出到结果目录
    pool = multiprocessing.Pool(processes=3)
    for pyc_file in out_pyc_files:
        # 单线程
        # ht.reverse_pyc(pyc_file, out_dir)

        # 多线程
        # t = threading.Thread(target=ht.reverse_pyc, args=(pyc_file, out_dir))
        # t.start()

        # 多进程
        # p = multiprocessing.Process(target=ht.reverse_pyc, args=(pyc_file, out_dir))
        # p.start()

        # 进程池
        pool.apply_async(ht.reverse_pyc, args=(pyc_file, out_dir))
    pool.close()
    pool.join()


def make_encrypto_exe_package_files():
    #### 转换解密文件
    ht = HexTool(struct_file_path)
    # 转换入口文件
    out_pyc_files.append(ht.make_main_pyc(main_file_path))

    # 转换依赖包文件
    package_files = os.listdir(extracted_package_dir)
    # print(package_files)
    for file in package_files:
        # 过滤依赖文件,这里简单过滤
        if file.endswith(".pyc.encrypted") and len(file.split(".")) == 3 and not file.startswith("_"):
            file_path = os.path.join(extracted_package_dir, file)
            # 这里要先解密文件 解密为pyc文件
            key = ht.get_encrypto_key(key_file_path)
            ht.decrypt_package_file(key, file_path, str(file_path).replace(".pyc.encrypted", ""))
            ht.make_main_pyc(str(file_path).replace(".pyc.encrypted", ""))
            out_pyc_files.append(str(file_path).replace(".encrypted", ""))

    #### 逆向还原文件，然后输出到结果目录
    pool = multiprocessing.Pool(processes=3)
    for pyc_file in out_pyc_files:
        # 单线程
        # ht.reverse_pyc(pyc_file, out_dir)

        # 多线程
        # t = threading.Thread(target=ht.reverse_pyc, args=(pyc_file, out_dir))
        # t.start()

        # 多进程
        # p = multiprocessing.Process(target=ht.reverse_pyc, args=(pyc_file, out_dir))
        # p.start()

        # 进程池
        pool.apply_async(ht.reverse_pyc, args=(pyc_file, out_dir))
    pool.close()
    pool.join()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: reverse_pyexe xxx.exe")
        sys.exit(-1)

    try:
        import uncompyle6
    except ImportError:
        print("[-] 未安装模块[uncompyle6]")
        print("[*] 请先安装模块[uncompyle6]")
        sys.exit(-1)

    ### 逆向exe文件
    re_flag = reverse_main(exe_file_path)
    if re_flag:
        os.chdir(root_path)
        # 获取入口文件
        main_file = get_main_file()
        main_file_path = os.path.join(extracted_dir, main_file)  # 入口文件路径
        # main_file_path = os.path.join(root_path, main_file_path)  # 入口文件 绝对路径
        # 转换出的pyc文件列表
        out_pyc_files = []

        ### 判断是否有加密
        if os.listdir(extracted_package_dir)[2].endswith(".encrypted"):
            make_encrypto_exe_package_files()
        else:
            make_exe_package_files()



