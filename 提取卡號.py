def luhn_checksum(card_number):
    """
    實現Luhn算法檢查信用卡號是否有效
    """
    digits = [int(d) for d in str(card_number)]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    
    total = sum(odd_digits)
    for digit in even_digits:
        total += sum(divmod(digit * 2, 10))
        
    return total % 10 == 0

def generate_valid_card_numbers(prefix, suffix):
    """
    生成所有可能的有效信用卡號
    參數:
    - prefix: 卡號的前綴數字 (字串，可以是6位或8位)
    - suffix: 卡號的後四位數字 (字串)
    """
    valid_numbers = []
    
    # 去除所有空格
    prefix = prefix.replace(" ", "")
    suffix = suffix.replace(" ", "")
    
    # 確認輸入長度正確
    if len(prefix) not in [6, 8] or len(suffix) != 4:
        print(f"錯誤: 前綴必須是6位或8位數 (當前: {len(prefix)}位)，後綴必須是4位數 (當前: {len(suffix)}位)")
        return valid_numbers
    
    # 確認輸入都是數字
    if not (prefix.isdigit() and suffix.isdigit()):
        print("錯誤: 前綴和後綴必須都是數字")
        return valid_numbers
    
    # 根據前綴長度決定中間部分的位數和可能組合數
    if len(prefix) == 6:
        middle_length = 6
        total_combinations = 1000000
    else:  # 前綴是8位
        middle_length = 4
        total_combinations = 10000
    
    progress_step = total_combinations // 20  # 每5%顯示一次進度
    
    print(f"正在生成可能的卡號組合，共{total_combinations}種可能...")
    
    # 生成所有中間位數字的組合
    count = 0
    for i in range(total_combinations):
        # 將i轉換為中間位數字字串，不足位數前面補0
        middle = f"{i:0{middle_length}d}"
        
        # 組合完整卡號
        card_number = prefix + middle + suffix
        
        # 檢查是否有效
        if luhn_checksum(card_number):
            valid_numbers.append(card_number)
        
        # 顯示進度
        count += 1
        if count % progress_step == 0:
            progress = (count / total_combinations) * 100
            print(f"進度: {progress:.1f}%")
    
    return valid_numbers

def format_card_number(card_number):
    """
    將信用卡號格式化為每4位一組，用空格分隔
    """
    return ' '.join([card_number[i:i+4] for i in range(0, len(card_number), 4)])

def main():
    print("信用卡號生成器")
    print("此程式會生成所有可能的有效信用卡號，基於已知的頭部數字和尾四位數字")
    print("頭部數字可以是6位或8位")
    
    prefix = input("請輸入卡號的頭部數字 (6位或8位): ")
    suffix = input("請輸入卡號的尾四位數字: ")
    
    valid_numbers = generate_valid_card_numbers(prefix, suffix)
    
    if valid_numbers:
        output_choice = input(f"找到 {len(valid_numbers)} 個有效卡號。要顯示在螢幕上還是儲存到檔案？(顯示/儲存): ").lower()
        
        if output_choice.startswith('顯') or output_choice == 'show' or output_choice == 's':
            print("\n有效的卡號:")
            for i, number in enumerate(valid_numbers, 1):
                print(f"{i}. {format_card_number(number)}")
        else:
            filename = input("請輸入要儲存的檔案名: ") or "valid_card_numbers.txt"
            with open(filename, 'w') as f:
                for number in valid_numbers:
                    f.write(format_card_number(number) + '\n')
            print(f"已將所有 {len(valid_numbers)} 個有效卡號儲存至 {filename}")
    else:
        print("沒有找到有效的卡號組合")

if __name__ == "__main__":
    main()
