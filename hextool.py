# -*- coding: utf-8 -*-
# @Time : 2021/12/16 16:12
# @Author : ordar
# @Project : reverse_pyexe
# @File : hex_tool.py
# @Python: 3.7.5
import os
import re
import sys


class HexTool:

    def __init__(self, struct_file):
        self.hex_header = self.get_hex_header(struct_file)

    @staticmethod
    def get_file_hex(file):
        """
        读取文件hex
        :param file:
        :return:
        """
        if os.path.exists(file):
            with open(file, 'rb') as f:
                file_hex = f.read().hex()
            return file_hex
        else:
            print("[-] {}文件不存在".format(file))
            sys.exit(0)

    def get_hex_header(self, struct_file):
        """
        获取文件头信息
        :param struct_file:
        :return:
        """
        return self.get_file_hex(struct_file)[0:32]

    def make_main_pyc(self, main_file, out_main_file=""):
        """
        将入口文件还原为pyc文件
        :param main_file: 入口文件
        :param out_main_file: 输出文件，默认为原文件名的pyc文件
        :return:
        """
        old_file_hex = self.get_file_hex(main_file)
        new_file_hex = self.hex_header + old_file_hex
        if not out_main_file:
            out_main_file = main_file + ".pyc"
        with open(out_main_file, 'wb') as f:
            f.write(bytes.fromhex(new_file_hex))
            print("[+] {} 转换为 {}".format(main_file, out_main_file))
        return out_main_file

    def make_package_pyc(self, package_file, out_package_file=""):
        """
        将依赖文件还原
        :param package_file: 依赖文件
        :param out_package_file:
        :return:
        """
        old_file_hex = self.get_file_hex(package_file)
        new_file_hex = self.hex_header + old_file_hex[24:]
        if not out_package_file:
            out_package_file = package_file
        with open(out_package_file, 'wb') as f:
            f.write(bytes.fromhex(new_file_hex))
            if package_file == out_package_file:
                print("[+] {} 转换完成".format(package_file))
            else:
                print("[+] {} 转换为 {}".format(package_file, out_package_file))
        return out_package_file

    def reverse_pyc(self, pyc_file, out_dir):
        """
        逆向还原pyc文件为py文件
        :param pyc_file:
        :param out_dir:
        :return:
        """
        py_file = os.path.basename(os.path.splitext(pyc_file)[0]) + ".py"
        py_file_path = os.path.join(out_dir, py_file)
        # print(py_file)
        recode = os.system("uncompyle6 -o {} {}".format(py_file_path, pyc_file))
        # print(recode, type(recode))
        if recode == 0:
            print("[+] {} 成功还原为py文件: {}".format(pyc_file, py_file_path))

    def get_encrypto_key(self, key_file):
        """
        获取加密的秘钥key
        :param key_file: pyimod00_crypto_key文件
        :return:
        """
        with open(key_file, "rb") as f:
            file_contenet = f.read()
            file_contenet_hex = file_contenet.hex()
            # print(file_contenet)
            # print(file_contenet_hex)
            key_hex = re.findall(r"5a10(.*?)4e29", file_contenet_hex)[0]
            # print(key_hex)
            key = bytes.fromhex(key_hex).decode()
            return key

    def decrypt_package_file(self, key, encrypted_file, out_pyc_file=""):
        """
        根据key将加密的依赖包文件解密为pyc文件
        :param key:
        :param encrypted_file:
        :param out_pyc_file:
        :return:
        """
        import tinyaes,zlib
        f = open(encrypted_file, 'rb')
        data = f.read()
        cipher = tinyaes.AES(key.encode(), data[:16])
        output = cipher.CTR_xcrypt_buffer(data[16:])
        f.close()
        output = zlib.decompress(output)
        if not out_pyc_file:
            out_pyc_file = str(encrypted_file).replace(".encrypted", "")
        with open(out_pyc_file, 'wb') as f:
            f.write(output)


if __name__ == '__main__':
    h = HexTool("struct")
    # print(h.get_file_hex("struct"))
    # print(h.get_hex_header("struct"))
    #
    # print(h.get_file_hex("host_scan.pyc"))
    # print(h.get_file_hex("host_scan.pyc")[24:])
    #
    # # print(h.make_main_pyc("worm"))
    # print(h.make_package_pyc("host_scan.pyc"))
    # print(h.reverse_pyc(r"D:\py_project\reverse_pyexe\worm.pyc", r"D:\py_project\reverse_pyexe\worm.exe_out"))
    # print(h.get_encrypto_key("aaaa.exe_extracted\\pyimod00_crypto_key"))
    print(h.make_main_pyc('guess'))