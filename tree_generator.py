import zipfile
from pathlib import Path

def compress_zip_structure(zip_path):
    structure = []  # Массив для хранения структуры
    id_counter = 1   # Начинаем с 1
    path_to_id = {'/': 0}  # Корень

    # Открываем ZIP-архив
    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        for info in zip_file.infolist():
            # Получаем полный путь к файлу/директории
            full_path = info.filename

            # Разбиваем путь на части
            path_parts = list(Path(full_path).parts)

            # Устанавливаем родительский путь
            parent_path = '/'.join(path_parts[:-1])+'/' if len(path_parts) > 1 else None

            # Добавляем директорию в словарь, если она еще не добавлена
            if full_path not in path_to_id and full_path[-1] == '/':
                current_id = id_counter
                path_to_id[full_path] = current_id
                id_counter += 1

                # Если есть родительский путь, добавляем его в словарь
                if parent_path and parent_path not in path_to_id:
                    path_to_id[parent_path] = id_counter
                    id_counter += 1

            # Добавляем запись для текущего элемента
            if  full_path[-3:] == '.py' or full_path[-1] == '/':
                if parent_path is not None:
                    parent_id = path_to_id.get(parent_path, 0)

                    if full_path[-1] == '/':  # Если это папка
                        current_id = path_to_id[full_path]
                        structure.append((parent_id, Path(info.filename).name, current_id))
                    else:  # Если это файл
                        structure.append(
                            (parent_id, Path(info.filename).name, 0))  # Здесь 0 для файлов, так как у них нет current_id
                else:
                    if full_path[-1] == '/':
                        current_id = path_to_id[full_path]
                        structure.append((0, Path(info.filename).name, current_id))
                    else:
                        structure.append((0, Path(info.filename).name, 0))  # Здесь 0 для файлов

    # Формируем "сжатую" структуру
    compressed_structure = []
    for parent_id, name, current_id in structure:
        compressed_structure.append(f"{parent_id}->{name}->{current_id}") if current_id else compressed_structure.append(f"{parent_id}->{name}")

    # Объединяем все в одну строку
    compressed_output = ";".join(compressed_structure)
    return compressed_output

# Пример использования
zip_file_path = "./mnt/data/2020.2-Anunbis-develop.zip"  # Путь к ZIP-архиву
compressed_structure = compress_zip_structure(zip_file_path)

# Выводим результат
print(compressed_structure)
