"""Extractor de evidencia (solo lectura) para la Skill auditoria-modelos.

Lee un .ipynb o .py y emite, de forma determinista, un inventario con referencias
estables `celda N (id X), l. L` y las señales que la Skill debe revisar. No ejecuta
ni modifica el archivo auditado.

Uso: python extraer_evidencia.py <archivo.ipynb|.py> [--json]
"""
import ast, json, re, sys
from pathlib import Path

PATRONES = {
    "split": r"\btrain_test_split\s*\(",
    "cv": r"\b(StratifiedKFold|KFold|GroupKFold|TimeSeriesSplit|cross_val_score|cross_validate|GridSearchCV|RandomizedSearchCV)\b",
    "fit_transform": r"\.fit_transform\s*\(",
    "fit": r"\.fit\s*\(",
    "pipeline": r"\b(Pipeline|make_pipeline|ColumnTransformer)\b",
    "transformador": r"\b(StandardScaler|MinMaxScaler|RobustScaler|SimpleImputer|KNNImputer|OneHotEncoder|OrdinalEncoder|PCA|SelectKBest)\b",
    "metrica": r"\b(accuracy_score|balanced_accuracy_score|precision_score|recall_score|f1_score|fbeta_score|roc_auc_score|confusion_matrix|classification_report|\.score\s*\()",
    "division_por_columna": r"/\s*df\w*\s*\[",
    "rng_global": r"\brng\.\w+\(",
    "estimador_sin_semilla": r"\b(RandomForestClassifier|RandomForestRegressor|DecisionTreeClassifier|GradientBoostingClassifier|ExtraTreesClassifier)\s*\((?![^)]*random_state)",
}

# Patrón multilínea: columna construida con np.where sobre una condición de otra columna
# (candidata a derivarse del objetivo). Se busca sobre la celda completa.
DERIVADA = re.compile(r"(\w+\[['\"][\w ]+['\"]\])\s*=\s*np\.where\(\s*(\w+\[['\"][\w ]+['\"]\])\s*==")


def celdas(ruta):
    p = Path(ruta)
    if p.suffix == ".ipynb":
        nb = json.loads(p.read_text(encoding="utf-8"))
        n = 0
        for c in nb["cells"]:
            if c["cell_type"] != "code":
                continue
            n += 1
            src = "".join(c["source"]) if isinstance(c["source"], list) else c["source"]
            yield n, c.get("id", "-"), src, c.get("outputs", [])
    else:
        yield 1, "script", p.read_text(encoding="utf-8"), []


def main(ruta, como_json=False):
    inv = {"archivo": ruta, "celdas_codigo": 0, "celdas_sin_salida": [], "errores": [], "senales": {k: [] for k in list(PATRONES) + ["derivada_de_otra_columna"]}}
    for n, cid, src, outs in celdas(ruta):
        inv["celdas_codigo"] += 1
        ref = f"celda {n} (id {cid})"
        if not outs and src.strip():
            inv["celdas_sin_salida"].append(ref)
        for o in outs:
            if o.get("output_type") == "error":
                inv["errores"].append(f"{ref}: {o.get('ename')}: {o.get('evalue')}")
        for m in DERIVADA.finditer(src):
            l = src[:m.start()].count("\n") + 1
            inv["senales"]["derivada_de_otra_columna"].append(f"{ref}, l. {l}: {m.group(1)} = np.where({m.group(2)} == ...)")
        for i, linea in enumerate(src.splitlines(), 1):
            for clave, pat in PATRONES.items():
                if re.search(pat, linea):
                    inv["senales"][clave].append(f"{ref}, l. {i}: {linea.strip()[:110]}")
    if como_json:
        print(json.dumps(inv, ensure_ascii=False, indent=1))
        return
    print(f"# Inventario de evidencia: {ruta}\nCeldas de código: {inv['celdas_codigo']}")
    print(f"Celdas de código sin salida: {len(inv['celdas_sin_salida'])}")
    print("Errores en salidas:", *(inv["errores"] or ["ninguno"]), sep="\n  ")
    for clave, lista in inv["senales"].items():
        print(f"\n[{clave}] {len(lista)}")
        for e in lista:
            print("  " + e)


if __name__ == "__main__":
    main(sys.argv[1], "--json" in sys.argv)
