from typing import List
from slither import Slither
from slither.core.declarations import FunctionContract
from slither.core.variables import StateVariable

API_KEY = "HPXNN2GP4VFJIBD4USI8QJF6MFI75HRQZT"


def detect_msg_sender_dependent(name: str, address: str) -> bool:
    slither = Slither(target=address, etherscan_api_key=API_KEY, disable_solc_warnings=True)
    main_contract = slither.get_contract_from_name(name)
    assert len(main_contract) == 1, f"No Contract Or Multiple Contracts Named {name}"
    main_contract = main_contract[0]
    # 获取在构造函数中，被msg.sender污染的变量
    constructors:List[FunctionContract] = main_contract.constructors
    msg_sender_state_var_taint = []
    for constructor in constructors:
        sol_vars = constructor.all_solidity_variables_read()
        for sol_var in sol_vars:
            if sol_var.name == "msg.sender":
                # 当前构造函数对状态变量的写操作
                msg_sender_state_var_taint.extend(constructor.all_state_variables_written())

    # 获取所有conditional state variable
    all_conditional_state_variables:List[StateVariable] = []
    for fn in main_contract.functions_and_modifiers:
        all_conditional_state_variables.extend(fn.all_conditional_state_variables_read())


    # 检查二者是否有相交的元素
    for msg_sender_state_var in msg_sender_state_var_taint:
        if msg_sender_state_var in all_conditional_state_variables:
            return True

    return False




if __name__ == '__main__':
    name = "AlgocracyDAO"
    address = "0xd329cd36665dcbb312d539cee1022b8e67ec7c1d"
    res = detect_msg_sender_dependent(name, address)
    print(res)
