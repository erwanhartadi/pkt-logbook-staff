// Harness uji: menjalankan blok CORE dari pemotong-kalender.html di Node.
// Pemakaian: node run_pemotong.mjs <html> <mulai> <selesai> <email|-> <keluar.zip> <input...>
import { readFileSync, writeFileSync } from "node:fs";
import { basename } from "node:path";

const [html, mulai, selesai, email, keluar, ...inputs] = process.argv.slice(2);
const src = readFileSync(html, "utf8");
const core = src.split("// ==== CORE-START")[1].split("// ==== CORE-END")[0];
const { proses } = new Function(core + "\nreturn { proses };")();
const files = inputs.map(p => {
  const b = readFileSync(p);
  return { name: basename(p), arrayBuffer: async () => b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength) };
});
const r = await proses(files, mulai, selesai, email === "-" ? "" : email);
writeFileSync(keluar, r.zip);
console.log(JSON.stringify({ laporan: r.laporan, ukuran: r.ukuran }));
