import zipfile
from pathlib import Path

# Функция для сохранения структуры ZIP-архива в виде списка с id, name и parent
def save_zip_structure_to_array(zip_path):
    structure = []  # Массив для хранения структуры
    id_counter = 1
    path_to_id = {"/": 0}  # Словарь для хранения соответствия пути и ID, корень указывает на id 0

    # Открываем ZIP-архив
    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        for info in zip_file.infolist():
            # Получаем полный путь и разбиваем его на части
            is_dir = info.is_dir()

            # Определяем родительский путь
            parent_path = str(Path(info.filename).parent).strip("/") or "/"  # Корень, если нет родителя
            parent_path = parent_path.replace('\\', '/')
            parent_id = path_to_id.get(parent_path)

            # Генерируем уникальный ID для текущего элемента
            current_id = id_counter
            id_counter += 1

            # Создаем запись для текущего элемента
            entry = {
                'id': current_id,
                'name': Path(info.filename).name,
                'parent': parent_id
            }

            # Добавляем запись в структуру
            structure.append(entry)

            # Сохраняем соответствие пути и ID
            # Если это директория, сохраняем ее ID
            if is_dir:
                path_to_id[str(info.filename).strip("/")] = current_id

    return structure

# Пример использования
zip_file_path = "mnt/data/luncher-api-master.zip"  # Путь к ZIP-архиву
zip_structure = save_zip_structure_to_array(zip_file_path)

# Выводим структуру
import pprint
pprint.pprint(zip_structure)
