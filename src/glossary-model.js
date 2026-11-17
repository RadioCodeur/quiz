export const normalizeTerm=value=>String(value??'').normalize('NFD').replace(/\p{M}/gu,'').toLocaleLowerCase('fr');
export function filterTerms(terms,query='',category='') {
  const words=normalizeTerm(query).trim().split(/\s+/u).filter(Boolean);
  return terms.filter(term=>(!category||term.category===category)&&words.every(word=>normalizeTerm(`${term.fr} ${term.en} ${term.definition}`).includes(word)));
}
