# Reglas de Cursor para IA Adaptiera

Esta carpeta contiene las reglas modulares de Cursor organizadas por tipo y contexto, permitiendo un desarrollo más eficiente y consistente del proyecto IA Adaptiera.

## 📁 Estructura de Reglas

### Reglas Globales (type: Always)
Estas reglas se aplican en todo el proyecto, independientemente del archivo o carpeta:

- **`general_coding_standards.mdc`**: Estándares de codificación, documentación y estilo
- **`project_structure.mdc`**: Estructura de carpetas y ubicación de archivos
- **`naming_conventions.mdc`**: Convenciones de nombrado
- **`error_handling.mdc`**: Manejo de errores y excepciones
- **`security_performance.mdc`**: Directrices de seguridad y rendimiento

### Reglas Contextuales (type: Auto Attached)
Estas reglas se activan automáticamente según los patrones de archivos:

- **`app_rules.mdc`**: Reglas específicas para archivos en `app/**`
- **`agents_rules.mdc`**: Reglas específicas para archivos en `agents/**`
- **`services_rules.mdc`**: Reglas específicas para archivos en `services/**`
- **`core_rules.mdc`**: Reglas específicas para archivos en `core/**`
- **`tests_rules.mdc`**: Reglas específicas para archivos en `tests/**`

## 🎯 Cómo Funcionan

1. **Reglas Globales**: Se aplican siempre que trabajas en cualquier archivo del proyecto
2. **Reglas Contextuales**: Se activan automáticamente cuando abres o trabajas en archivos de carpetas específicas
3. **Combinación**: Cursor combina las reglas globales con las contextuales relevantes

## 🚀 Beneficios

- **Organización**: Reglas específicas por contexto
- **Mantenibilidad**: Fácil actualización de reglas específicas
- **Consistencia**: Aplicación automática según el tipo de archivo
- **Eficiencia**: Solo las reglas relevantes se aplican en cada contexto


## 🔧 Personalización

Para modificar reglas específicas:

1. Identifica el archivo `.mdc` relevante
2. Edita las reglas según tus necesidades
3. Las reglas se aplicarán automáticamente en Cursor

## 📚 Referencias

- **Archivo principal**: `.cursorrules` en la raíz contiene reglas consolidadas
- **Estructura del proyecto**: `estructura.md` en la raíz
- **Configuración**: Archivos como `.flake8`, `mypy.ini` complementan estas reglas 