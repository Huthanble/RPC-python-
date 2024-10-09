my_list = [1, 2, 3, 4, 5]
element_to_remove = 1

my_list.remove(element_to_remove)
my_list.append(element_to_remove)

print(my_list)  # 输出：[1, 2, 4, 5]
