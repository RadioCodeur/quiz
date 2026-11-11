export const COURSE_ORDER = ['python-scientifique', 'audio-signal', 'pytorch', 'audio-ml', 'generation-controle', 'evaluation-recherche'];
export const COURSE_STORAGE_KEY = 'a-lecoute.courses.v1';

export function courseHref(themeId, chapterId, questionId) {
  const params = new URLSearchParams({ theme: themeId });
  if (questionId) params.set('question', questionId);
  return `./cours.html?${params}${chapterId ? `#${encodeURIComponent(chapterId)}` : ''}`;
}

export function buildCoverage(courses) {
  const coverage = new Map();
  for (const course of courses) for (const chapter of course.chapters) {
    for (const id of chapter.questionIds) coverage.set(id, { themeId: course.themeId, chapterId: chapter.id });
  }
  return coverage;
}

export function wordCount(value) {
  return String(value).trim().split(/\s+/u).filter(Boolean).length;
}

export function chapterMinutes(chapter) {
  const text = chapterText(chapter);
  // Includes time to read examples and diagrams; indicative, never a timer.
  return Math.max(3, Math.ceil(wordCount(text) / 150));
}

export function chapterText(chapter) {
  const blocks=chapter.blocks.map(block=>[
    block.text,block.title,block.caption,block.goal,block.result,block.introduction,block.explanation,block.variant?.change,block.variant?.explanation,
    ...(block.items??[]),
    ...(block.steps??[]).flatMap(step=>[step.title,step.text]),
    ...(block.nodes??[]).flatMap(node=>[node.title,node.text]),
    ...(block.panels??[]).flatMap(panel=>[panel.title,...panel.items]),
  ].filter(Boolean).join(' '));
  return [...Object.values(chapter.progression??chapter.context??{}),...(chapter.notions??[]).flatMap(notion=>[notion.name,notion.explanation]),...blocks,chapter.checkpoint?.prompt,chapter.checkpoint?.explanation].filter(Boolean).join(' ');
}

export function courseStage(course,chapterId) {
  return course.journey?.stages.find(stage=>stage.chapterIds.includes(chapterId))??null;
}

export function chapterNavigation(course,chapter) {
  const sequence=chapter.readingRole==='reference'?course.chapters:course.chapters.filter(item=>item.readingRole!=='reference');
  const index=sequence.indexOf(chapter);
  return {previous:sequence[index-1]??null,next:sequence[index+1]??null};
}

export function mergeCourseReferences(base,courses) {
  return [...new Map([...base,...courses.flatMap(course=>course.references??[])].map(source=>[source.id,source])).values()];
}

export function normalizeProgress(raw, courses) {
  const valid = new Set(courses.flatMap(c => c.chapters.map(ch => `${c.themeId}/${ch.id}`)));
  const completed = Array.isArray(raw?.completed) ? [...new Set(raw.completed.filter(key => valid.has(key)))] : [];
  const last = raw?.last && valid.has(`${raw.last.themeId}/${raw.last.chapterId}`) ? { themeId: raw.last.themeId, chapterId: raw.last.chapterId } : null;
  return { version: 1, completed, last, readingMode: raw?.readingMode === true, largeText: raw?.largeText === true };
}

export function setChapterRead(progress, themeId, chapterId, read) {
  const key = `${themeId}/${chapterId}`;
  const completed = new Set(progress.completed);
  read ? completed.add(key) : completed.delete(key);
  return { ...progress, completed: [...completed] };
}

export function resolveChapter(course, { chapterId, questionId } = {}) {
  return course.chapters.find(ch => ch.id === chapterId)
    ?? course.chapters.find(ch => ch.questionIds.includes(questionId))
    ?? course.chapters[0];
}
