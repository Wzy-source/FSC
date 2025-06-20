import os


# 调用gigahorse，执行自定义的datalog文件，判断是否存在IsFactory.csv文件
def detect_factory(file_path: str) -> bool:
    # 构造命令，执行自定义factory.dl文件
    command = (
        f"../gigahorse-toolchain/gigahorse.py "
        f"--timeout_secs=300 "
        f"-C ../datalog/factory.dl "
        f"{file_path}"
    )
    # 执行gigahourse
    os.system(command)
    # 判断out文件夹是否输出IsFactory文件
    contract_name = os.path.splitext(os.path.basename(file_path))[0]
    is_factory_file = os.path.join(".", ".temp", contract_name, "out", "IsFactory.csv")
    if os.path.exists(is_factory_file) and os.path.getsize(is_factory_file) > 0:
        # 如果不是工厂，gigahorse会创建一个空的IsFactory.csv文件
        print(f"INFO: Found non-empty IsFactory.csv. Contract '{contract_name}' is a factory.")
        return True

    print(f"INFO: IsFactory.csv not found or is empty. Contract '{contract_name}' is not a factory.")
    return False


if __name__ == '__main__':
    file_path = "../tests/factory/ERC1155SeaDropCloneFactory.hex"
    detect_factory(file_path)
