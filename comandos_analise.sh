#!/usr/bin/env bash
# ------------------------------------------------------------
# comandos_analise.sh
# Consolida os comandos de análise dos runs xlarge/xxlarge.
# Uso:
#   bash comandos_analise.sh [DIRETORIO_DE_LOGS]
# Exemplo:
#   bash comandos_analise.sh logs/verificacao_xlarge_xxlarge
# ------------------------------------------------------------
set -euo pipefail

LOGDIR="${1:-logs/verificacao_xlarge_xxlarge}"
OUTDIR="$LOGDIR"

if [ ! -d "$LOGDIR" ]; then
  echo "ERRO: diretório '$LOGDIR' não existe." >&2
  exit 1
fi

echo ">> Saída será gerada em: $OUTDIR"
mkdir -p "$OUTDIR"

# 1) Extrai FO1 e Tempo dos arquivos *.resumo.txt e cria CSV consolidado
#    Formato: instancia,arquivo,FO1,Tempo(s)
echo ">> [1/6] Gerando $OUTDIR/resumo.csv a partir de *.resumo.txt ..."
awk -F': *' 'BEGIN{
    print "instancia,arquivo,FO1,Tempo(s)"
  }
  /FO1[:=]/{fo1=$2}
  /Tempo/{t=$2; gsub(" s","",t);
    inst = (FILENAME ~ /xxlarge/) ? "xxlarge" : "xlarge";
    print inst "," FILENAME "," fo1 "," t
  }' "$LOGDIR"/*_run*_*.resumo.txt | sort > "$OUTDIR/resumo.csv"

# 2) Estatísticas estendidas por instância (média, mediana, dp, min, max)
echo ">> [2/6] Calculando estatísticas (stats_ext.csv) ..."
python - <<'PY'
import csv, statistics as s, math
from collections import defaultdict
import sys
p = sys.argv[1]
rows = list(csv.reader(open(p, newline='', encoding='utf-8')))
by = defaultdict(lambda: {'t':[], 'fo':[]})
for r in rows[1:]:
    inst, _, fo, t = r[0], r[1], float(r[2]), float(r[3])
    by[inst]['t'].append(t); by[inst]['fo'].append(fo)
out = sys.argv[2]
with open(out, "w", newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(["instancia","runs","FO1_media","FO1_mediana","Tempo_media","Tempo_mediana","Tempo_min","Tempo_max","Tempo_dp"])
    for inst in sorted(by):
        t = by[inst]['t']; fo = by[inst]['fo']
        tempo_dp = (s.pstdev(t) if len(t)>1 else 0.0)
        w.writerow([inst, len(t),
                    f"{sum(fo)/len(fo):.2f}", f"{s.median(fo):.2f}",
                    f"{sum(t)/len(t):.2f}", f"{s.median(t):.2f}",
                    f"{min(t):.2f}", f"{max(t):.2f}", f"{tempo_dp:.2f}"])
PY "$OUTDIR/resumo.csv" "$OUTDIR/stats_ext.csv"

# 3) Visualizações (boxplot de tempo por instância e scatter FO1 x tempo)
echo ">> [3/6] Gerando gráficos (PNG) ..."
python - <<'PY'
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from collections import defaultdict
import sys
p = sys.argv[1]
rows = list(csv.reader(open(p, newline='', encoding='utf-8')))
# Boxplot Tempo por instância
times = defaultdict(list)
for r in rows[1:]:
    times[r[0]].append(float(r[3]))
labels = sorted(times)
data = [times[k] for k in labels]
plt.figure()
plt.boxplot(data, labels=labels)
plt.ylabel("Tempo (s)")
plt.title("Tempo por instância")
plt.savefig(sys.argv[2], dpi=150, bbox_inches='tight')
plt.close()
# Dispersão FO1 x Tempo
xs, ys, cs = [], [], []
for r in rows[1:]:
    cs.append(r[0]); ys.append(float(r[2])); xs.append(float(r[3]))
plt.figure()
for inst in sorted(set(cs)):
    xi = [x for x,c in zip(xs,cs) if c==inst]
    yi = [y for y,c in zip(ys,cs) if c==inst]
    plt.scatter(xi, yi, label=inst)
plt.xlabel("Tempo (s)"); plt.ylabel("FO1"); plt.legend(); plt.title("FO1 vs Tempo")
plt.savefig(sys.argv[3], dpi=150, bbox_inches='tight')
plt.close()
PY "$OUTDIR/resumo.csv" "$OUTDIR/tempo_boxplot.png" "$OUTDIR/fo1_vs_tempo.png"

# 4) Extrai tempo incremental por iteração a partir de logs do xxlarge
echo ">> [4/6] Extraindo tempo incremental por iteração (xxlarge) ..."
if compgen -G "$LOGDIR/xxlarge_run*.log" > /dev/null; then
  awk '
    /\[Iteração/ {
      if (match($0, /Tempo acumulado = ([0-9.]+)s/, a)) {
        t=a[1]+0;
        if (++cnt[FILENAME] > 1) {
          inc = t - prev[FILENAME];
          printf "%s,%d,%.2f\n", FILENAME, cnt[FILENAME]-1, inc
        }
        prev[FILENAME]=t
      }
    }
  ' "$LOGDIR"/xxlarge_run*.log > "$OUTDIR/per_iter_xxlarge.csv"

  echo "Top 15 maiores incrementos (possíveis gargalos):" > "$OUTDIR/per_iter_xxlarge_top15.txt"
  sort -t, -k3,3nr "$OUTDIR/per_iter_xxlarge.csv" | head -n 15 >> "$OUTDIR/per_iter_xxlarge_top15.txt"
else
  echo "Aviso: não encontrei logs do padrão '$LOGDIR/xxlarge_run*.log'. Pulando etapa 4."
fi

# 5) Mostra as tabelas no terminal (opcional) e salva em .pretty.txt
echo ">> [5/6] Salvando versões formatadas (.pretty.txt) das tabelas ..."
{
  echo "# resumo.csv"
  column -s, -t "$OUTDIR/resumo.csv" || cat "$OUTDIR/resumo.csv"
  echo
  echo "# stats_ext.csv"
  column -s, -t "$OUTDIR/stats_ext.csv" || cat "$OUTDIR/stats_ext.csv"
} > "$OUTDIR/tabelas.pretty.txt"

# 6) Relatório Markdown simples com links para arquivos gerados
echo ">> [6/6] Gerando relatório Markdown ..."
REPORT="$OUTDIR/relatorio.md"
python - <<'PY'
import csv, sys, datetime, pathlib
outdir = pathlib.Path(sys.argv[1])
def csv_to_md(path):
    import csv
    rows = list(csv.reader(open(path, newline='', encoding='utf-8')))
    if not rows: return ""
    hdr = "| " + " | ".join(rows[0]) + " |\n"
    sep = "| " + " | ".join(["---"]*len(rows[0])) + " |\n"
    body = "".join("| " + " | ".join(r) + " |\n" for r in rows[1:])
    return hdr + sep + body
md = []
md.append("# Relatório de Verificação (xlarge vs xxlarge)\n")
md.append(f"*Gerado em:* {datetime.datetime.now().isoformat(timespec='seconds')}\n")
md.append("## Estatísticas\n")
md.append(csv_to_md(outdir / "stats_ext.csv"))
md.append("\n## Gráficos\n")
md.append(f"![Tempo por instância](./tempo_boxplot.png)\n\n")
md.append(f"![FO1 vs Tempo](./fo1_vs_tempo.png)\n\n")
if (outdir / "per_iter_xxlarge_top15.txt").exists():
    md.append("## Maiores incrementos por iteração (xxlarge)\n")
    md.append("```\n" + open(outdir / "per_iter_xxlarge_top15.txt", encoding='utf-8').read() + "\n```\n")
open(outdir / "relatorio.md", "w", encoding="utf-8").write("".join(md))
PY "$OUTDIR"

echo ">> Pronto! Arquivos gerados:"
ls -1 "$OUTDIR"/{resumo.csv,stats_ext.csv,tabelas.pretty.txt,tempo_boxplot.png,fo1_vs_tempo.png,relatorio.md} 2>/dev/null || true
[ -f "$OUTDIR/per_iter_xxlarge.csv" ] && echo "$OUTDIR/per_iter_xxlarge.csv" || true
[ -f "$OUTDIR/per_iter_xxlarge_top15.txt" ] && echo "$OUTDIR/per_iter_xxlarge_top15.txt" || true

echo
echo "DICA: anexe o arquivo '$OUTDIR/relatorio.md' (e as imagens) no seu envio."
