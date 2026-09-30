class ClipBoard {
  async copy(content: string) {
    try {
      const decodedContent = this.decodeContent(content);
      await navigator.clipboard.writeText(decodedContent);
      console.log("Contenu copié dans le presse-papiers");
    } catch (err) {
      console.error("Échec de la copie : ", err);
    }
  }

  private decodeContent(content: string): string {
    // Liste des entités HTML à décoder
    const entities = {
      '&lt;': '<',
      '&gt;': '>',
      '&amp;': '&',
      '&quot;': '"',
      '&apos;': "'",
      '&#39;': "'",
      '&#x27;': "'"
    };

    // Remplace chaque entité HTML par son caractère correspondant
    let decodedContent = content;
    for (const [entity, char] of Object.entries(entities)) {
      decodedContent = decodedContent.replace(new RegExp(entity, 'g'), char);
    }

    return decodedContent;
  }
}

const clipboard = new ClipBoard();
export default clipboard;
