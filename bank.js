export async function loadBank() {
  const base = `${import.meta.env.BASE_URL}data/`;
  const read = async file => {
    const response = await fetch(base + file);
    if (!response.ok) throw new Error(`Chargement impossible : ${file}`);
    return response.json();
  };
  const themes = await read('themes.json');
  const [groups, refs] = await Promise.all([
    Promise.all(themes.map(t => read(t.file))),
    Promise.all(['sources-python-pytorch.json', 'sources-audio.json', 'sources-generation-research.json'].map(read)),
  ]);
  const bank = groups.flat();
  if (bank.length !== 200 || new Set(bank.map(q => q.id)).size !== 200) throw new Error('La banque de questions est incomplète.');
  return { bank, themes, sources: refs.flat() };
}
