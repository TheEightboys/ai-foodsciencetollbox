/**
 * Helper functions to format content for display to match document formatting
 */

export function capitalizeGradeLevel(gradeLevel: string): string {
  if (!gradeLevel) return gradeLevel;
  
  const gradeLower = gradeLevel.toLowerCase().trim();
  const gradeMapping: Record<string, string> = {
    'elementary': 'Elementary',
    'middle': 'Middle',
    'middle school': 'Middle School',
    'high': 'High',
    'high school': 'High School',
    'college': 'College',
  };
  
  if (gradeLower in gradeMapping) {
    return gradeMapping[gradeLower];
  }
  
  return gradeLevel.charAt(0).toUpperCase() + gradeLevel.slice(1);
}

export function capitalizeTopic(topic: string): string {
  if (!topic) return topic;
  return topic.charAt(0).toUpperCase() + topic.slice(1);
}

export function stripMetadataFromContent(content: string): string {
  // Guard against null/undefined content
  if (!content || typeof content !== 'string') return '';
  // Remove metadata lines that AI might have included (Grade Level, Time Needed, Topic)
  // Also remove generation type titles (Lesson Objectives, Lesson Starter, Bell Ringer)
  const lines = content.split('\n');
  const filteredLines: string[] = [];
  let skipNextEmpty = false; // Flag to skip empty line after metadata
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const lineTrimmed = line.trim();
    const lineLower = lineTrimmed.toLowerCase();
    
    // Skip lines that look like metadata (case-insensitive, with or without value)
    // Match patterns like:
    // - "Grade Level: middle"
    // - "Grade Level:"
    // - "Time Needed: 3-5 minutes"
    // - "Topic: protein"
    // - "Category: food_science"
    // - "LESSON STARTER IDEAS"
    if (
      lineLower.match(/^grade level:\s*/) ||
      lineLower.match(/^time needed:\s*/) ||
      lineLower.match(/^topic:\s*/) ||
      lineLower.match(/^category:\s*/)
    ) {
      skipNextEmpty = true;
      continue; // Skip this line
    }
    
    // Also check for lines that start with just the label (no colon, might be formatting artifact)
    if (
      lineLower === 'grade level' ||
      lineLower === 'time needed' ||
      lineLower === 'topic' ||
      lineLower === 'category' ||
      lineLower.startsWith('grade level ') ||
      lineLower.startsWith('time needed ') ||
      lineLower.startsWith('topic ') ||
      lineLower.startsWith('category ')
    ) {
      // Only skip if it's a standalone line (not part of a sentence)
      if (lineTrimmed.length < 50) { // Short lines are likely metadata
        skipNextEmpty = true;
        continue;
      }
    }
    
    // Skip generation type titles that appear after metadata
    // "Lesson Objectives", "Lesson Starter", "Bell Ringer", "Today's Bell Ringer",
    // "Lesson Starter Ideas", "LESSON STARTER IDEAS", "Discussion Questions"
    if (
      lineLower === 'lesson objectives' ||
      lineLower === 'lesson starter' ||
      lineLower === 'lesson starter ideas' ||
      lineLower === 'discussion questions' ||
      lineLower.startsWith('lesson objectives') ||
      lineLower.startsWith('lesson starter ideas') ||
      lineLower.startsWith('lesson starter') ||
      lineLower.startsWith('discussion questions')
    ) {
      // Only skip if it's a standalone title (short line)
      if (lineTrimmed.length < 50) {
        skipNextEmpty = true;
        continue;
      }
    }
    
    // Remove "(Section header: ...)" text that AI might include
    // This appears in prompts like "(Section header: Arial 14pt, bold)"
    if (lineLower.includes('(section header')) {
      // Remove the entire line if it's just the section header instruction
      if (/^\s*\(section header[^)]*\)\s*$/i.test(lineTrimmed)) {
        continue;
      }
      // Otherwise, remove just the "(Section header: ...)" part from the line
      const cleanedLine = line.replace(/\(section header[^)]*\)/gi, '').trim();
      if (!cleanedLine) {
        continue;
      }
      filteredLines.push(cleanedLine);
      continue;
    }
    
    // Skip empty line after metadata (common formatting)
    if (skipNextEmpty && !lineTrimmed) {
      skipNextEmpty = false;
      continue;
    }
    
    skipNextEmpty = false;
    filteredLines.push(line); // Keep original line (with original spacing)
  }
  
  return filteredLines.join('\n').trim();
}

export function formatContentWithMetadata(
  content: string,
  gradeLevel: string,
  topic: string,
  timeNeeded?: string
): string {
  // Guard against null/undefined content
  if (!content || typeof content !== 'string') content = '';
  // First, strip any metadata that AI might have included
  const cleanedContent = stripMetadataFromContent(content);
  
  const capitalizedGrade = capitalizeGradeLevel(gradeLevel);
  const capitalizedTopic = capitalizeTopic(topic);
  
  let formatted = '';
  
  // Add Grade Level (bold label in display)
  formatted += `**Grade Level:** ${capitalizedGrade}\n`;
  
  // Add Topic (bold label in display)
  formatted += `**Topic:** ${capitalizedTopic}\n\n`;
  
  // Add the cleaned content (without duplicate metadata)
  formatted += cleanedContent;
  
  return formatted;
}

