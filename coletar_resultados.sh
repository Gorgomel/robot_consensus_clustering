#!/usr/bin/env bash
# Coleta resultados dos *.resumo.txt, consolida CSVs e imprime tabelas.
# Uso: bash coletar_resultados.sh [DIR_LOGS]
# Ex.: bash coletar_resultados.sh logs/verificacao_xlarge_xxlarge
set -euo pipefail

DIR="${1:-logs/verificacao_xlarge_xxlarge}"
OUT="$DIR"

echo ">> Saída será gerada em: $OUT"
mkdir -p "$OUT"

# 1) Consolidar arquivos resumo -> resumo.csv  (Arquivo,FO1,Tempo(s))
echo ">> [1/3] Gerando $OUT/resumo.csv a partir de *.resumo.txt ..."
# Observação: Tempo vem como 'NNN.s' ou 'NNN s', então removemos ' s'.
# O arquivo tem nome .../xlarge_runN_YYYYmmdd-HHMMSS.resumo.txt
# Mantemos linha: caminho,FO1,Tempo(s)
if ls "$DIR"/*_run*_*.resumo.txt >/dev/null 2>&1; then
  awk -F': *' '
    /FO1[:=]/{fo1=$2}
    /Tempo/{t=$2; gsub(" s","",t); print FILENAME "," fo1 "," t}
  ' "$DIR"/*_run*_*.resumo.txt \
  | sort > "$OUT/resumo.csv"
else
  echo "ERRO: não encontrei arquivos *_run*_*.resumo.txt em $DIR" >&2
  exit 1
fi

# Tabela “bonita” do resumo
{ echo "Arquivo,FO1,Tempo(s)"; cat "$OUT/resumo.csv"; } > "$OUT/resumo_header.csv"
column -s, -t "$OUT/resumo_header.csv" > "$OUT/tabela_resumo.txt"

# 2) Deduplicar por run (mantém o arquivo com timestamp mais recente por run)
#    Chave = caminho sem o sufixo _YYYYmmdd-HHMMSS.resumo.txt
echo ">> [2/3] Deduplicando por run (resumo_dedup.csv) ..."
awk -F, '
  {
    file=$1
    key=file
    sub(/_[0-9-]+\.resumo\.txt$/, "", key)  # remove sufixo com timestamp
    # Mantém o mais recente (ordem lexicográfica do nome do arquivo já inclui timestamp)
    if (!(key in best_file) || file > best_file[key]) {
      best_file[key]=file
      best_row[key]=$0
    }
  }
  END { for (k in best_row) print best_row[k] }
' "$OUT/resumo.csv" \
| sort > "$OUT/resumo_dedup.csv"

{ echo "Arquivo,FO1,Tempo(s)"; cat "$OUT/resumo_dedup.csv"; } > "$OUT/resumo_dedup_header.csv"
column -s, -t "$OUT/resumo_dedup_header.csv" > "$OUT/tabela_resumo_dedup.txt"

# 3) Estatísticas por instância (xlarge/xxlarge) usando o arquivo deduplicado
echo ">> [3/3] Calculando estatísticas (stats.csv) ..."
awk -F, '
  {
    f=$1; fo=$2+0; t=$3+0
    inst = (f ~ /xxlarge/) ? "xxlarge" : "xlarge"
    n[inst]++; sumT[inst]+=t; sumFO[inst]+=fo
    if (!(inst in minT) || t < minT[inst]) minT[inst]=t
    if (t > maxT[inst]) maxT[inst]=t
  }
  END {
    print "instancia,runs,FO1_medio,Tempo_medio,Tempo_min,Tempo_max"
    for (i in n) printf "%s,%d,%.2f,%.2f,%.2f,%.2f\n",
                       i, n[i], sumFO[i]/n[i], sumT[i]/n[i], minT[i], maxT[i]
  }
' "$OUT/resumo_dedup.csv" \
| sort -t, -k1,1 > "$OUT/stats.csv"

column -s, -t "$OUT/stats.csv" > "$OUT/tabela_stats.txt"

echo "------------------------------------------------------------"
echo "Arquivos gerados em $OUT:"
echo "  - resumo.csv                 (consolidado bruto)"
echo "  - tabela_resumo.txt          (tabela bonitinha)"
echo "  - resumo_dedup.csv           (1 linha por run)"
echo "  - tabela_resumo_dedup.txt"
echo "  - stats.csv                  (estatísticas por instância)"
echo "  - tabela_stats.txt"
echo "------------------------------------------------------------"
echo "Pronto! Envie-me os CSVs e/ou as tabelas .txt acima."
