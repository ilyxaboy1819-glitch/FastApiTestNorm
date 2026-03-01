# src/schemas/__init__.py

# 1. Импортируем все схемы, чтобы они стали известны Python
from .user import UserRead, UserCreate, UserUpdate
from .profile import ProfileRead, ProfileCreate, ProfileUpdate
from .role import RoleRead, RoleCreate, RoleUpdate
from .application import ApplicationRead, ApplicationCreate, ApplicationUpdate
from .category import CategoryRead, CategoryCreate, CategoryUpdate
from .comment import CommentRead, CommentCreate, CommentUpdate

# 2. Явно перестраиваем модели в правильном порядке,
#    чтобы Pydantic разрешил все forward-ссылки.
#    Это эквивалентно вызову .model_rebuild() для каждого класса.
#    Порядок важен: сначала самые "глубокие", потом те, которые на них ссылаются.

# Самостоятельные модели (ни на кого не ссылаются)
CategoryRead.model_rebuild()
RoleRead.model_rebuild()

# Модели, которые ссылаются друг на друга
CommentRead.model_rebuild()
ApplicationRead.model_rebuild()
ProfileRead.model_rebuild()
UserRead.model_rebuild()

# Для Create/Update схем обычно не требуется, но можно и их для порядка
UserCreate.model_rebuild()
ApplicationCreate.model_rebuild()
# ... остальные по желанию

# Эта строка не обязательна, но показывает, что файл загружен
print("✅ Pydantic схемы успешно перестроены")