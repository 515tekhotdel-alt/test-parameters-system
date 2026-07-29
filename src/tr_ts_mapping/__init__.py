"""
Модуль маппинга требований ТР ТС
"""

from .chemistry.material_chemicals import (
    load_material_chemicals,
    get_chemicals_for_material,
    get_all_materials,
    get_material_by_keyword,
    extract_materials_from_text
)

from .chemistry.chemistry_norms import (
    load_chemistry_norms,
    get_norm_for_substance
)

from .biology.biology_by_layer import (
    load_biology_by_layer,
    get_biology_for_layer
)

from .biology.biology_by_product_type import (
    load_biology_by_product_type,
    get_biology_for_product_type
)