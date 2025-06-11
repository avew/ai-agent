# System and User Prompt Configuration

## Overview

Aplikasi sekarang mendukung konfigurasi penuh prompt melalui environment variables:
- `SYSTEM_PROMPT`: Mengatur perilaku dan karakter AI assistant
- `USER_PROMPT_TEMPLATE`: Mengatur format presentasi context dan query ke AI

Ini memberikan fleksibilitas maksimal untuk menyesuaikan interaksi tanpa mengubah kode.

## Configuration

### Environment Variables

Tambahkan ke file `.env` Anda:

```bash
# System prompt - mengatur perilaku AI
SYSTEM_PROMPT=Your custom system prompt here

# User prompt template - mengatur format presentasi
USER_PROMPT_TEMPLATE=Your custom template with {context} and {query} placeholders
```

### Required Placeholders

User prompt template HARUS menggunakan placeholders:
- `{context}`: Akan diganti dengan konteks dari knowledge base
- `{query}`: Akan diganti dengan pertanyaan user

### Default Values

Jika environment variables tidak diset, aplikasi menggunakan default:

**SYSTEM_PROMPT:**
```
Kamu adalah asisten AI yang membantu menjawab pertanyaan berdasarkan knowledge base yang diberikan. 
Gunakan informasi dari konteks yang relevan untuk memberikan jawaban yang akurat dan informatif. 
Jika informasi tidak tersedia dalam konteks, sampaikan bahwa informasi tersebut tidak ada dalam knowledge base.
```

**USER_PROMPT_TEMPLATE:**
```
Konteks dari knowledge base:
{context}

Pertanyaan: {query}

Berikan jawaban yang jelas dan akurat berdasarkan konteks di atas.
```

## Examples

### Contoh 1: Formal Business Assistant
```bash
SYSTEM_PROMPT="Anda adalah konsultan bisnis profesional untuk perusahaan enterprise. Berikan analisis strategis dan rekomendasi bisnis berdasarkan knowledge base perusahaan."

USER_PROMPT_TEMPLATE="Data dan informasi perusahaan:\n{context}\n\nPertanyaan strategis: {query}\n\nBerikan analisis profesional dengan rekomendasi yang dapat diimplementasikan."
```

### Contoh 2: Technical Documentation Helper
```bash
SYSTEM_PROMPT="You are a senior technical documentation specialist. Provide precise, actionable technical guidance based on official documentation."

USER_PROMPT_TEMPLATE="Technical Documentation:\n{context}\n\nTechnical Question: {query}\n\nProvide step-by-step technical guidance with code examples where applicable."
```

### Contoh 3: Educational Assistant
```bash
SYSTEM_PROMPT="Kamu adalah tutor berpengalaman yang sabar dan komunikatif. Jelaskan konsep dengan cara yang mudah dipahami dan berikan contoh praktis."

USER_PROMPT_TEMPLATE="Materi pembelajaran:\n{context}\n\nPertanyaan siswa: {query}\n\nJelaskan dengan cara yang mudah dipahami, berikan contoh konkret, dan sertakan tips pembelajaran."
```

### Contoh 4: Research Assistant
```bash
SYSTEM_PROMPT="You are a research analyst with expertise in academic literature review. Provide comprehensive, evidence-based analysis with proper attribution."

USER_PROMPT_TEMPLATE="Research Papers and Data:\n{context}\n\nResearch Question: {query}\n\nProvide a comprehensive analysis with citations and evidence-based conclusions."
```

### Contoh 5: Customer Support
```bash
SYSTEM_PROMPT="Kamu adalah customer support specialist yang ramah dan solution-oriented. Fokus pada penyelesaian masalah customer dengan cepat dan efektif."

USER_PROMPT_TEMPLATE="Knowledge Base dan FAQ:\n{context}\n\nPertanyaan Customer: {query}\n\nBerikan solusi yang jelas, langkah-langkah yang mudah diikuti, dan alternatif jika diperlukan."
```

### Contoh 6: Creative Writing Assistant
```bash
SYSTEM_PROMPT="You are a creative writing mentor with expertise in storytelling and narrative development. Help users improve their writing with constructive feedback."

USER_PROMPT_TEMPLATE="Writing Resources and Examples:\n{context}\n\nWriter's Question: {query}\n\nProvide creative guidance with examples, techniques, and actionable suggestions for improvement."
```

## Best Practices

### System Prompt
1. **Keep it Concise**: System prompt yang terlalu panjang dapat mengurangi efektivitas
2. **Be Specific**: Definisikan dengan jelas peran dan batasan AI assistant
3. **Consider Domain**: Sesuaikan dengan domain knowledge base Anda
4. **Language Consistency**: Pastikan bahasa prompt konsisten dengan expected interaction

### User Prompt Template
1. **Use Required Placeholders**: Selalu gunakan `{context}` dan `{query}`
2. **Clear Structure**: Buat struktur yang jelas untuk konteks dan pertanyaan
3. **Appropriate Formatting**: Gunakan `\n` untuk line breaks dalam environment variable
4. **Contextual Instructions**: Tambahkan instruksi spesifik tentang bagaimana menggunakan context
5. **Output Guidance**: Berikan panduan tentang format jawaban yang diharapkan

### Testing and Optimization
1. **Test Different Combinations**: Eksperimen dengan kombinasi system dan user prompt
2. **Monitor Response Quality**: Evaluasi kualitas respons dengan prompt yang berbeda
3. **A/B Testing**: Test prompt yang berbeda untuk use case spesifik
4. **User Feedback**: Kumpulkan feedback untuk optimisasi prompt

## Implementation Details

- Kedua prompt dimuat saat aplikasi startup melalui `SearchService.__init__()`
- Perubahan environment variable memerlukan restart aplikasi
- System prompt dan user prompt template disimpan sebagai instance variables
- User prompt template menggunakan Python `.format()` method dengan placeholders
- Validation untuk required placeholders dilakukan saat runtime

## Troubleshooting

### Prompt Tidak Berubah
- Pastikan file `.env` sudah diupdate dengan kedua variables
- Restart aplikasi Flask
- Verify environment variables terload dengan checking logs

### Response Quality Menurun
- Review kedua prompt untuk clarity dan consistency
- Test dengan kombinasi prompt yang berbeda
- Ensure user prompt template menggunakan placeholders yang benar

### Template Error
- Pastikan `{context}` dan `{query}` placeholders ada dalam USER_PROMPT_TEMPLATE
- Check untuk typo dalam placeholder names
- Verify escape characters untuk newlines (`\n`)

### Formatting Issues
- Gunakan `\n` instead of actual line breaks dalam environment variable
- Escape special characters jika diperlukan
- Test template formatting sebelum production deployment

## Related Configuration

Environment variables terkait lainnya:
- `CHAT_MODEL`: Model OpenAI yang digunakan
- `MAX_CONTEXT_LENGTH`: Maksimum panjang context per chunk
- `DEFAULT_TOP_K`: Jumlah document chunks yang diambil
- `SYSTEM_PROMPT`: AI assistant behavior configuration
- `USER_PROMPT_TEMPLATE`: Context and query presentation format
