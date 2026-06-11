export interface Fallacy {
	code: string;
	name_en: string;
	name_id: string;
	short_description: string;
	full_description: string;
	example_id: string;
	how_to_counter: string;
	severity: 'high' | 'medium' | 'low';
	category: 'relevance' | 'presumption' | 'ambiguity' | 'emotional' | 'causal';
	color_hex: string;
	icon_emoji: string;
}

export const FALLACIES: Fallacy[] = [
	{
		code: 'ad_hominem',
		name_en: 'Ad Hominem',
		name_id: 'Ad Hominem (Menyerang Pribadi)',
		short_description: 'Menyerang karakter, kepribadian, atau latar belakang lawan bicara alih-alih menyanggah argumennya secara logis.',
		full_description: 'Ad Hominem terjadi ketika seseorang menolak suatu argumen bukan karena isi argumen tersebut salah, melainkan karena ada aspek negatif pada diri orang yang menyampaikannya. Hal ini merupakan cacat logika karena kebenaran suatu pernyataan tidak bergantung pada siapa yang mengatakannya.\n\nDalam diskusi publik, fallacy ini sering digunakan untuk merusak kredibilitas lawan agar audiens mengabaikan poin penting yang disampaikannya. Ini adalah bentuk pengalihan isu yang sangat umum.',
		example_id: 'Jangan percaya pendapat politisi itu tentang kebijakan ekonomi baru. Dia kan pernah gagal dalam mengelola bisnisnya sendiri beberapa tahun lalu.',
		how_to_counter: 'Tunjukkan secara tenang bahwa latar belakang atau karakter Anda tidak memengaruhi validitas data atau argumen ekonomi yang Anda sampaikan, lalu ajak kembali fokus ke pokok bahasan.',
		severity: 'high',
		category: 'relevance',
		color_hex: '#DA2B22',
		icon_emoji: '👤'
	},
	{
		code: 'strawman',
		name_en: 'Strawman',
		name_id: 'Strawman (Jerami Palsu)',
		short_description: 'Menyalahartikan atau mendistorsi argumen lawan agar terlihat lemah atau ekstrem, sehingga lebih mudah diserang.',
		full_description: 'Strawman fallacy dilakukan dengan cara membuat "orang-orangan jerami"—yaitu versi argumen lawan yang sudah diubah, disederhanakan, atau dilebih-lebihkan—lalu menyerang versi palsu tersebut. Tujuannya adalah membuat argumen sendiri terlihat jauh lebih unggul dan benar secara mutlak.\n\nDengan memanipulasi posisi lawan, pelaku fallacy menghindari keharusan menyanggah poin asli yang sebenarnya lebih kuat dan bernuansa. Ini menciptakan ilusi kemenangan intelektual di depan audiens.',
		example_id: 'Pihak oposisi meminta anggaran militer dievaluasi. Itu artinya mereka ingin membiarkan negara kita tanpa pertahanan dan membiarkan musuh menjajah kita!',
		how_to_counter: 'Klarifikasi kembali argumen asli Anda dengan tegas. Katakan, "Saya tidak mengatakan kita harus meniadakan pertahanan, melainkan mengevaluasi efisiensi anggarannya agar tepat sasaran."',
		severity: 'high',
		category: 'relevance',
		color_hex: '#A4161A',
		icon_emoji: '🌾'
	},
	{
		code: 'false_dilemma',
		name_en: 'False Dilemma',
		name_id: 'False Dilemma (Dilema Palsu)',
		short_description: 'Menyajikan situasi seolah-olah hanya ada dua pilihan ekstrem yang tersedia, padahal ada alternatif lain di antara keduanya.',
		full_description: 'Dilema Palsu (atau Black-or-White Thinking) memaksa audiens untuk memilih satu dari dua opsi yang biasanya bersifat polar. Taktik ini menyembunyikan spektrum pilihan atau jalan tengah yang sebenarnya tersedia dan logis.\n\nBiasanya, salah satu opsi dibuat sangat buruk sehingga audiens terpaksa memilih opsi yang diinginkan oleh pembicara. Ini sering digunakan dalam pidato politik untuk menciptakan urgensi artifisial atau loyalitas buta.',
		example_id: 'Kalau kamu tidak mendukung pembangunan pabrik semen baru di daerah ini, berarti kamu ingin melihat warga lokal selamanya hidup dalam kemiskinan dan tanpa lapangan kerja.',
		how_to_counter: 'Sebutkan opsi-opsi alternatif ketiga, keempat, atau kelima yang ada. Tunjukkan bahwa kemajuan ekonomi daerah bisa dicapai lewat sektor pariwisata atau pertanian tanpa merusak lingkungan.',
		severity: 'high',
		category: 'presumption',
		color_hex: '#BA181B',
		icon_emoji: '⚖️'
	},
	{
		code: 'slippery_slope',
		name_en: 'Slippery Slope',
		name_id: 'Slippery Slope (Lereng Licin)',
		short_description: 'Mengklaim bahwa satu langkah kecil akan memicu serangkaian peristiwa buruk yang ekstrem tanpa bukti hubungan sebab-akibat yang kuat.',
		full_description: 'Slippery Slope mengasumsikan bahwa jika peristiwa A terjadi, maka B, C, dan akhirnya skenario bencana Z pasti akan menyusul secara berantai. Argumen ini mengeksploitasi ketakutan audiens terhadap hasil akhir yang ekstrem.\n\nKelemahan logisnya terletak pada tidak adanya bukti yang membuktikan bahwa setiap langkah dalam rantai tersebut tidak dapat dihindari. Sering kali, ada banyak titik kontrol di mana proses tersebut bisa dihentikan.',
		example_id: 'Kalau pemerintah melegalkan transportasi online hari ini, maka besok transportasi konvensional akan punah, lalu jutaan sopir menganggur, kriminalitas meroket, dan akhirnya ekonomi negara runtuh total.',
		how_to_counter: 'Tanyakan bukti atau mekanisme konkret yang menghubungkan langkah awal langsung ke konsekuensi ekstrem tersebut. Tunjukkan titik-titik regulasi yang bisa mencegah bencana itu terjadi.',
		severity: 'medium',
		category: 'causal',
		color_hex: '#E5383B',
		icon_emoji: '📉'
	},
	{
		code: 'appeal_to_authority',
		name_en: 'Appeal to Authority',
		name_id: 'Appeal to Authority (Argumen Otoritas)',
		short_description: 'Mengklaim sesuatu benar hanya karena seorang tokoh terkenal atau otoritas mengatakannya, tanpa didukung bukti konkret.',
		full_description: 'Argumen Otoritas menjadi cacat logika ketika opini seorang ahli di satu bidang digunakan untuk membenarkan klaim di bidang lain yang tidak relevan, atau ketika pendapat ahli tersebut tidak mewakili konsensus ilmiah yang ada.\n\nMempercayai keahlian seseorang adalah hal yang wajar, namun keahlian tersebut bukanlah jaminan kebenaran mutlak. Kebenaran suatu argumen tetap harus dinilai berdasarkan bukti empiris dan logika internalnya.',
		example_id: 'Aktor terkenal itu menyatakan di media sosial bahwa vaksin jenis ini berbahaya bagi jantung. Karena dia publik figur yang pintar, pasti apa yang dikatakannya benar.',
		how_to_counter: 'Ingatkan bahwa keahlian sang tokoh bukan di bidang kesehatan. Ajukan pertanyaan tentang bukti klinis atau konsensus dari institusi medis resmi yang mempelajari masalah tersebut.',
		severity: 'medium',
		category: 'relevance',
		color_hex: '#D97706',
		icon_emoji: '🎓'
	},
	{
		code: 'appeal_to_emotion',
		name_en: 'Appeal to Emotion',
		name_id: 'Appeal to Emotion (Argumen Emosi)',
		short_description: 'Menggunakan manipulasi emosi (takut, iba, benci, bangga) alih-alih argumen logis untuk memengaruhi keyakinan seseorang.',
		full_description: 'Appeal to Emotion terjadi saat argumen rasional digantikan oleh bahasa yang bermuatan emosional tinggi. Tujuannya adalah membuat lawan bicara atau audiens bertindak atas dasar perasaan yang meluap-luap, bukan analisis logis.\n\nMeskipun emosi adalah bagian dari komunikasi manusia, ia tidak bisa dijadikan alat bukti kebenaran ilmiah atau keadilan hukum. Fallacy ini sangat sering digunakan dalam kampanye politik dan iklan komersial.',
		example_id: 'Bagaimana mungkin Anda menuntut terdakwa korupsi ini dihukum berat? Tidakkah Anda kasihan melihat anak-anaknya yang masih kecil terpaksa hidup tanpa kehadiran sosok ayah?',
		how_to_counter: 'Akui aspek emosionalnya secara empati, namun tegaskan bahwa hukum dan keadilan harus ditegakkan berdasarkan bukti dan undang-undang demi kemaslahatan publik yang lebih luas.',
		severity: 'medium',
		category: 'emotional',
		color_hex: '#EA580C',
		icon_emoji: '❤️'
	},
	{
		code: 'bandwagon',
		name_en: 'Bandwagon / Ad Populum',
		name_id: 'Bandwagon (Ikut-ikutan)',
		short_description: 'Mengklaim bahwa suatu gagasan atau tindakan benar hanya karena mayoritas orang memercayai atau melakukannya.',
		full_description: 'Bandwagon (atau Ad Populum) bersandar pada insting sosial manusia untuk menyesuaikan diri dengan kelompok. Cacat logis ini mengasumsikan bahwa popularitas setara dengan kebenaran atau validitas.\n\nDalam sejarah, banyak hal yang diyakini oleh mayoritas orang ternyata salah (seperti keyakinan bahwa bumi itu datar). Menilai validitas gagasan semata-mata dari jumlah pengikutnya mengabaikan kebutuhan akan investigasi objektif.',
		example_id: 'Semua orang di kantor ini menggunakan software bajakan itu untuk mempercepat pekerjaan mereka. Jadi, tindakan kita menyalinnya sekarang tidak bisa dibilang melanggar hukum.',
		how_to_counter: 'Tunjukkan bahwa kebenaran dan legalitas tindakan bersifat mandiri dari popularitasnya. Katakan, "Banyaknya orang yang melakukan pelanggaran tidak membuat tindakan tersebut menjadi benar."',
		severity: 'medium',
		category: 'relevance',
		color_hex: '#B45309',
		icon_emoji: '👥'
	},
	{
		code: 'circular_reasoning',
		name_en: 'Circular Reasoning',
		name_id: 'Circular Reasoning (Penalaran Melingkar)',
		short_description: 'Mengajukan premis yang sebenarnya merupakan kesimpulan itu sendiri, sehingga argumen berputar tanpa membuktikan apa pun.',
		full_description: 'Penalaran Melingkar terjadi ketika kesimpulan suatu argumen sudah diasumsikan kebenarannya dalam premis awal. Akibatnya, argumen tidak pernah beranjak dari titik awal dan tidak memberikan bukti eksternal baru.\n\nSecara struktur, argumen ini berbentuk "A benar karena B, dan B benar karena A". Ini adalah bentuk argumen yang tidak informatif dan tidak memiliki landasan logika yang kokoh.',
		example_id: 'Peraturan ini sangat adil dan wajib dipatuhi karena hukum dibuat demi menjamin keadilan bagi seluruh masyarakat tanpa terkecuali.',
		how_to_counter: 'Urai kelemahan strukturnya dengan menunjukkan bahwa argumen tersebut berputar-putar tanpa menjelaskan kriteria objektif mengapa hukum tersebut bisa disebut adil.',
		severity: 'high',
		category: 'presumption',
		color_hex: '#CA8A04',
		icon_emoji: '🔄'
	},
	{
		code: 'hasty_generalization',
		name_en: 'Hasty Generalization',
		name_id: 'Hasty Generalization (Generalisasi Terburu-buru)',
		short_description: 'Menarik kesimpulan umum yang luas berdasarkan sampel atau bukti yang sangat sedikit atau tidak representatif.',
		full_description: 'Generalisasi Terburu-buru terjadi ketika seseorang mengambil satu atau dua contoh kasus khusus dan langsung menyimpulkan bahwa seluruh populasi memiliki karakteristik yang sama. Ini mengabaikan variansi alami dan kaidah statistik.\n\nFallacy ini sering memicu stereotip prasangka rasial, gender, atau kelompok tertentu karena otak manusia cenderung menyederhanakan realitas demi menghemat energi kognitif.',
		example_id: 'Kemarin saya ditipu oleh penjual online asal kota X. Mulai sekarang, saya tidak mau lagi membeli apa pun dari pedagang yang berasal dari kota itu karena mereka semua penipu.',
		how_to_counter: 'Sebutkan bahwa satu atau dua kasus buruk tidak mewakili ribuan pedagang jujur di kota tersebut, dan ajak untuk melihat data atau ukuran sampel yang lebih besar.',
		severity: 'medium',
		category: 'presumption',
		color_hex: '#F59E0B',
		icon_emoji: '🏃'
	},
	{
		code: 'post_hoc',
		name_en: 'Post Hoc',
		name_id: 'Post Hoc (Sebab-Akibat Palsu)',
		short_description: 'Mengasumsikan bahwa karena peristiwa A terjadi sebelum peristiwa B, maka peristiwa A adalah penyebab langsung dari peristiwa B.',
		full_description: 'Post Hoc Ergo Propter Hoc secara harfiah berarti "setelah ini, maka karena ini". Cacat logika ini mengacaukan urutan kronologis dengan hubungan sebab-akibat yang nyata.\n\nHanya karena dua kejadian terjadi berurutan, tidak berarti ada korelasi kausal di antara keduanya. Sering kali ada faktor ketiga yang tidak terlihat, atau urutan tersebut hanyalah kebetulan belaka.',
		example_id: 'Setelah kami mengganti logo perusahaan bulan lalu, angka penjualan kami langsung naik 30%. Ini membuktikan bahwa bentuk logo baru mendatangkan hoki besar.',
		how_to_counter: 'Tunjukkan faktor-faktor eksternal lain yang mungkin memengaruhi kenaikan tersebut, seperti tren pasar musiman, kampanye iklan baru, atau promosi harga.',
		severity: 'medium',
		category: 'causal',
		color_hex: '#F97316',
		icon_emoji: '📅'
	},
	{
		code: 'red_herring',
		name_en: 'Red Herring',
		name_id: 'Red Herring (Pengalih Perhatian)',
		short_description: 'Memasukkan topik sampingan yang tidak relevan ke dalam diskusi untuk mengalihkan perhatian dari isu utama.',
		full_description: 'Red Herring diambil dari teknik melatih anjing pelacak menggunakan ikan herring merah yang berbau menyengat untuk mengalihkan penciuman mereka. Dalam debat, taktik ini digunakan ketika posisi seseorang terdesak.\n\nDengan memperkenalkan topik baru yang tampaknya menarik atau provokatif, pembicara berharap lawan bicaranya akan mengejar topik baru tersebut dan melupakan kegagalan argumen asli yang sedang didebatkan.',
		example_id: 'Kenapa kita sibuk mendebatkan korupsi dana bantuan sosial hari ini? Padahal kita harusnya lebih memikirkan ancaman kedaulatan laut kita yang sedang diganggu kapal asing!',
		how_to_counter: 'Akui pentingnya topik kedaulatan laut tersebut secara singkat, lalu tarik kembali diskusi ke topik utama: "Topik itu penting, namun sekarang kita sedang membahas pertanggungjawaban dana bansos."',
		severity: 'high',
		category: 'relevance',
		color_hex: '#E67E22',
		icon_emoji: '🐟'
	},
	{
		code: 'false_equivalence',
		name_en: 'False Equivalence',
		name_id: 'False Equivalence (Kesetaraan Palsu)',
		short_description: 'Menyahkan dua hal memiliki nilai atau bobot yang sama, padahal keduanya memiliki perbedaan esensial yang signifikan.',
		full_description: 'Kesetaraan Palsu menyamakan dua hal yang tampak mirip di permukaan tetapi memiliki tingkat keparahan, skala, atau konteks moral yang jauh berbeda. Ini sering digunakan untuk meredam kritik.\n\nDalam jurnalisme, fallacy ini sering muncul dalam bentuk penyajian "dua sudut pandang secara berimbang" (bothsidesism) pada isu di mana salah satu pihak memiliki bukti ilmiah mutlak sedangkan pihak lainnya hanya mengandalkan mitos.',
		example_id: 'Mencuri sebungkus mi instan karena kelaparan di toko kelontong memiliki kesalahan moral yang sama persis dengan koruptor yang menilap miliaran dana bantuan bencana.',
		how_to_counter: 'Bedah perbedaan skala, niat, dampak sosial, dan konteks sistemik dari kedua perbuatan tersebut untuk membuktikan bahwa menyamakan keduanya adalah tidak proporsional.',
		severity: 'high',
		category: 'presumption',
		color_hex: '#D35400',
		icon_emoji: '⚖️'
	},
	{
		code: 'appeal_to_ignorance',
		name_en: 'Appeal to Ignorance',
		name_id: 'Appeal to Ignorance (Ketidaktahuan)',
		short_description: 'Menyatakan bahwa suatu klaim pasti benar karena belum ada yang bisa membuktikan bahwa klaim tersebut salah (atau sebaliknya).',
		full_description: 'Appeal to Ignorance (Argumentum ad Ignorantiam) menyandarkan kebenaran argumen pada kekosongan informasi atau bukti. Ketidakmampuan kita untuk membuktikan atau menyangkal sesuatu dijadikan "bukti" pendukung.\n\nLogika dasar menyatakan bahwa tiadanya bukti bukanlah bukti dari ketiadaan (absence of evidence is not evidence of absence). Klaim positif tetap membutuhkan beban pembuktian aktif.',
		example_id: 'Tidak ada satu pun ilmuwan yang bisa membuktikan secara mutlak bahwa alien tidak pernah mengunjungi bumi di masa lalu. Jadi, teori astronot kuno itu pasti benar.',
		how_to_counter: 'Jelaskan bahwa ketidakmampuan membuktikan sebaliknya tidak membuat suatu klaim otomatis menjadi benar. Sesuatu dinyatakan benar jika ada bukti positif yang menguatkannya.',
		severity: 'medium',
		category: 'presumption',
		color_hex: '#F39C12',
		icon_emoji: '👽'
	},
	{
		code: 'tu_quoque',
		name_en: 'Tu Quoque',
		name_id: 'Tu Quoque (Kamupun Juga)',
		short_description: 'Menghindari kritik dengan cara menyerang balik lawan menggunakan tuduhan bahwa mereka juga melakukan kesalahan yang sama.',
		full_description: 'Tu Quoque adalah variasi dari Ad Hominem yang menuduh lawan bersikap munafik. Argumen ini mencoba membatalkan kritik seseorang dengan menunjukkan bahwa perilaku kritikus tersebut tidak konsisten dengan apa yang ia khotbahkan.\n\nMeskipun kemunafikan adalah cacat karakter, hal itu tidak secara logis membatalkan kebenaran atau validitas kritik yang disampaikan. Kebenaran nasihat medis tentang bahaya merokok tetap valid bahkan jika dokter yang mengatakannya adalah perokok aktif.',
		example_id: 'Ayah menyuruhku berhenti merokok karena merusak paru-paru. Tapi Ayah sendiri merokok sebungkus sehari, jadi nasihat Ayah tidak usah kudengar.',
		how_to_counter: 'Akui inkonsistensi pelaku kritik jika perlu, lalu pisahkan dengan substansi kritik itu sendiri: "Perilaku Ayah mungkin keliru, tetapi data medis tentang bahaya rokok tetap nyata."',
		severity: 'medium',
		category: 'relevance',
		color_hex: '#B58900',
		icon_emoji: '🪞'
	},
	{
		code: 'burden_of_proof',
		name_en: 'Burden of Proof',
		name_id: 'Burden of Proof (Beban Pembuktian)',
		short_description: 'Memindahkan tanggung jawab membuktikan suatu klaim kepada orang lain yang meragukannya, alih-alih membuktikannya sendiri.',
		full_description: 'Beban Pembuktian (Onus Probandi) menetapkan bahwa siapa pun yang membuat klaim positif luar biasa bertanggung jawab penuh untuk menyajikan bukti. Fallacy ini terjadi ketika pembuat klaim menuntut penentangnya untuk membuktikan klaim tersebut salah.\n\nDalam metode ilmiah dan hukum, prinsip dasar menyatakan bahwa seseorang dianggap tidak bersalah atau suatu klaim dianggap belum terbukti sampai ada bukti positif yang dihadirkan.',
		example_id: 'Saya percaya ada teko teh gaib yang mengorbit matahari di antara bumi dan mars. Kalau kamu tidak percaya, buktikan kalau teko itu tidak ada!',
		how_to_counter: 'Tegaskan aturan logika dasar: "Beban pembuktian ada pada Anda yang membuat klaim adanya teko tersebut, bukan pada saya untuk membuktikan ketiadaannya."',
		severity: 'high',
		category: 'presumption',
		color_hex: '#159A5B',
		icon_emoji: '⚖️'
	},
	{
		code: 'black_or_white',
		name_en: 'Black-or-White Thinking',
		name_id: 'Black-or-White (Berpikir Dikotomis)',
		short_description: 'Menyederhanakan situasi kompleks menjadi dua kategori mutlak yang berlawanan tanpa ruang untuk opsi tengah.',
		full_description: 'Black-or-White Thinking (mirip dengan Dilema Palsu tetapi lebih berfokus pada cara pandang kognitif) membagi realitas secara ekstrem: baik atau buruk, kawan atau lawan, sukses atau gagal total.\n\nCara berpikir ini mengabaikan nuansa abu-abu dan kompleksitas yang menjadi ciri dari sebagian besar situasi kehidupan nyata. Hal ini membatasi pemecahan masalah yang kreatif.',
		example_id: 'Dalam konflik politik ini, kamu harus memilih memihak kubu kami sepenuhnya, atau kamu adalah musuh yang ingin menghancurkan bangsa ini.',
		how_to_counter: 'Tolak kategorisasi mutlak tersebut. Jelaskan posisi netral atau objektif Anda yang mendukung aspek baik dan mengkritik aspek buruk dari kedua belah pihak secara adil.',
		severity: 'medium',
		category: 'presumption',
		color_hex: '#16A085',
		icon_emoji: '🏁'
	},
	{
		code: 'appeal_to_nature',
		name_en: 'Appeal to Nature',
		name_id: 'Appeal to Nature (Kembali ke Alam)',
		short_description: 'Mengklaim bahwa sesuatu pasti baik karena bersifat "alami" atau buruk karena bersifat "buatan/kimiawi".',
		full_description: 'Appeal to Nature mengasumsikan secara keliru bahwa segala sesuatu yang alami memiliki kualitas moral atau manfaat kesehatan yang positif, sedangkan yang buatan manusia berbahaya. Ini adalah penyederhanaan yang keliru.\n\nFaktanya, banyak zat alami yang mematikan bagi manusia (seperti bisa ular atau jamur beracun), sedangkan banyak penemuan buatan manusia (seperti antibiotik dan vaksin) menyelamatkan jutaan nyawa.',
		example_id: 'Kamu tidak usah minum obat resep dokter yang penuh bahan kimia itu. Pakai saja ramuan daun herbal alami ini, karena yang alami pasti lebih aman bagi tubuh.',
		how_to_counter: 'Ingatkan bahwa alam juga menghasilkan racun mematikan, dan bahwa efektivitas obat medis telah diuji secara klinis di laboratorium terlepas dari asal bahan bakunya.',
		severity: 'low',
		category: 'emotional',
		color_hex: '#27AE60',
		icon_emoji: '🌿'
	},
	{
		code: 'anecdotal_evidence',
		name_en: 'Anecdotal Evidence',
		name_id: 'Anecdotal Evidence (Bukti Anekdot)',
		short_description: 'Menggunakan pengalaman pribadi atau satu kasus terisolasi alih-alih data ilmiah/statistik sebagai bukti kebenaran umum.',
		full_description: 'Bukti Anekdot sangat persuasif karena otak manusia lebih mudah mencerna cerita personal daripada grafik data kering. Namun, pengalaman individu tidak dapat mewakili tren populasi secara luas.\n\nSatu kasus luar biasa sering kali dipengaruhi oleh bias konfirmasi, kebetulan, atau placebo. Bukti anekdot hanya boleh digunakan sebagai pemantik hipotesis, bukan kesimpulan ilmiah akhir.',
		example_id: 'Kakek saya merokok dua bungkus sehari dan tetap hidup sehat sampai usia 90 tahun. Jadi, semua klaim dokter tentang bahaya merokok itu cuma omong kosong.',
		how_to_counter: 'Hormati umur panjang kakek tersebut sebagai kasus luar biasa (outlier), lalu tunjukkan data statistik dari jutaan perokok lain yang menderita penyakit kronis akibat kebiasaan tersebut.',
		severity: 'medium',
		category: 'presumption',
		color_hex: '#059669',
		icon_emoji: '🗣️'
	},
	{
		code: 'texas_sharpshooter',
		name_en: 'Texas Sharpshooter',
		name_id: 'Texas Sharpshooter (Membidik Target Palsu)',
		short_description: 'Memilih data yang mendukung hipotesis sendiri dan mengabaikan data lain yang membantahnya untuk menciptakan pola semu.',
		full_description: 'Nama fallacy ini diambil dari anekdot tentang seorang koboi yang menembaki dinding lumbung secara acak, lalu menggambar lingkaran target di sekitar lubang peluru terbanyak agar terlihat seperti penembak jitu.\n\nPelaku fallacy ini menyaring data secara selektif (cherry-picking) untuk menciptakan ilusi adanya hubungan sebab-akibat atau signifikansi statistik yang sebenarnya terjadi karena kebetulan.',
		example_id: 'Perusahaan minuman manis ini merilis riset yang menunjukkan bahwa konsumsi gula mereka meningkatkan fokus belajar anak di sekolah, dengan mengabaikan 10 riset lain yang menghubungkannya dengan obesitas.',
		how_to_counter: 'Tunjukkan sisa data yang diabaikan atau disembunyikan oleh pihak tersebut. Jelaskan pentingnya melihat seluruh kumpulan data (meta-analisis) untuk kesimpulan objektif.',
		severity: 'high',
		category: 'causal',
		color_hex: '#10B981',
		icon_emoji: '🎯'
	},
	{
		code: 'no_true_scotsman',
		name_en: 'No True Scotsman',
		name_id: 'No True Scotsman (Kesucian Kelompok)',
		short_description: 'Mengubah definisi keanggotaan kelompok secara sepihak untuk mengecualikan anggota yang perilakunya merusak klaim awal.',
		full_description: 'No True Scotsman terjadi ketika seseorang membuat generalisasi universal tentang suatu kelompok, lalu ketika dihadapkan pada contoh anggota kelompok yang melanggar klaim tersebut, mereka memodifikasi definisi kelompok dengan menambahkan kata "sejati".\n\nIni adalah taktik perlindungan argumen dari bantahan empiris demi menjaga kesucian atau reputasi kelompoknya di mata publik.',
		example_id: 'Orang Indonesia itu sangat ramah dan sopan. Kalau ada netizen Indonesia yang mencaci-maki di medsos, berarti dia bukanlah orang Indonesia sejati.',
		how_to_counter: 'Tunjukkan bahwa netizen tersebut secara hukum dan budaya tetaplah bagian dari kelompok warga Indonesia, dan menyangkal identitasnya tidak menyelesaikan masalah perilaku sosial.',
		severity: 'medium',
		category: 'ambiguity',
		color_hex: '#4A3E3D',
		icon_emoji: '🏴'
	},
	{
		code: 'genetic_fallacy',
		name_en: 'Genetic Fallacy',
		name_id: 'Genetic Fallacy (Kekeliruan Asal-usul)',
		short_description: 'Menilai kebaikan atau keburukan suatu argumen berdasarkan asal-usul, sejarah, atau dari mana gagasan tersebut bermula.',
		full_description: 'Genetic Fallacy mengabaikan validitas logis terkini dari suatu gagasan dan justru berfokus pada sejarah masa lalunya. Hal ini mirip dengan Ad Hominem tetapi ditujukan pada gagasan atau institusi, bukan individu.\n\nAsal-usul suatu hal memang penting untuk konteks sejarah, namun tidak menentukan kebenaran intrinsiknya saat ini. Sebuah teori ilmiah yang awalnya terinspirasi dari mimpi atau mitos mistis bisa tetap valid jika terbukti lewat eksperimen modern.',
		example_id: 'Ide tentang gotong-royong itu awalnya dikampanyekan oleh rezim masa lalu untuk memobilisasi massa secara paksa. Jadi, kita harus menolak nilai tersebut sekarang.',
		how_to_counter: 'Tegaskan bahwa meskipun sejarah asal-usulnya kontroversial, nilai atau konsep gotong-royong saat ini terbukti membawa dampak sosial positif bagi kerukunan warga.',
		severity: 'medium',
		category: 'relevance',
		color_hex: '#46444E',
		icon_emoji: '🧬'
	},
	{
		code: 'begging_the_question',
		name_en: 'Begging the Question',
		name_id: 'Begging the Question (Mengemis Pertanyaan)',
		short_description: 'Argumen yang asumsi dasarnya membutuhkan pembuktian lebih lanjut, namun disajikan seolah-olah sudah disepakati benar.',
		full_description: 'Begging the Question (Petitio Principii) sering dianggap sama dengan Circular Reasoning, namun lebih berfokus pada penyelundupan asumsi kontroversial ke dalam premis tanpa bukti. Kalimatnya sering kali menyamarkan klaim utama sebagai fakta mutlak.\n\nIstilah ini sering salah dipahami dalam bahasa Inggris populer sebagai "memancing pertanyaan baru", padahal makna logisnya adalah mengasumsikan apa yang seharusnya dibuktikan.',
		example_id: 'Tindakan hukuman mati harus dilarang karena pembunuhan berencana oleh negara merupakan tindakan yang tidak bermoral.',
		how_to_counter: 'Tunjukkan bahwa premis "hukuman mati adalah tindakan tidak bermoral" justru merupakan inti masalah yang sedang diperdebatkan dan perlu dibuktikan terlebih dahulu.',
		severity: 'high',
		category: 'presumption',
		color_hex: '#78350F',
		icon_emoji: '❓'
	},
	{
		code: 'loaded_question',
		name_en: 'Loaded Question',
		name_id: 'Loaded Question (Pertanyaan Menjebak)',
		short_description: 'Mengajukan pertanyaan yang memiliki asumsi praduga bersalah tersembunyi, sehingga jawaban apa pun akan membuat penjawab bersalah.',
		full_description: 'Pertanyaan Menjebak dirancang bukan untuk mendapatkan informasi objektif, melainkan untuk menggiring opini publik atau menjatuhkan lawan bicara. Di dalamnya terdapat premis bersalah yang tidak bisa ditolak dengan mudah.\n\nContoh klasik adalah pertanyaan interogatif yang memaksa jawaban ya atau tidak pada situasi di mana kedua jawaban tersebut membenarkan tuduhan tersembunyi.',
		example_id: 'Apakah Anda sudah berhenti memakai uang kas RT untuk keperluan pribadi Anda?',
		how_to_counter: 'Jangan jawab "ya" atau "tidak". Tolak asumsi di dalam pertanyaan tersebut secara langsung: "Saya tidak pernah menggunakan uang kas RT untuk keperluan pribadi saya."',
		severity: 'medium',
		category: 'presumption',
		color_hex: '#8C6239',
		icon_emoji: '💣'
	},
	{
		code: 'appeal_to_tradition',
		name_en: 'Appeal to Tradition',
		name_id: 'Appeal to Tradition (Argumen Tradisi)',
		short_description: 'Mengklaim bahwa suatu keyakinan atau metode pasti benar hanya karena sudah dilakukan sejak lama dari generasi ke generasi.',
		full_description: 'Appeal to Tradition (Argumentum ad Antiquitatem) mengasumsikan bahwa usia atau kelangsungan sejarah suatu praktik adalah bukti mutlak kebaikan atau efektivitasnya.\n\nMeskipun tradisi memiliki nilai budaya yang berharga, ia bukanlah ukuran kebenaran ilmiah atau moral. Banyak kebiasaan kuno (seperti perbudakan atau penolakan pendidikan bagi perempuan) yang dijalankan berabad-abad akhirnya terbukti keliru dan ditinggalkan.',
		example_id: 'Perusahaan kita harus tetap menggunakan sistem pembukuan kertas ini secara manual karena kita sudah menjalankannya sejak 30 tahun lalu dan terbukti aman.',
		how_to_counter: 'Tunjukkan perubahan zaman, kemajuan teknologi, dan efisiensi yang ditawarkan oleh metode modern tanpa harus meremehkan warisan sejarah masa lalu.',
		severity: 'low',
		category: 'emotional',
		color_hex: '#704214',
		icon_emoji: '🏛️'
	},
	{
		code: 'sunk_cost_fallacy',
		name_en: 'Sunk Cost Fallacy',
		name_id: 'Sunk Cost (Biaya Tertanam)',
		short_description: 'Melanjutkan keputusan atau proyek yang merugi hanya karena telah menginvestasikan banyak waktu, uang, atau tenaga di dalamnya.',
		full_description: 'Sunk Cost Fallacy adalah kecenderungan psikologis di mana seseorang menolak untuk menyerah pada usaha yang gagal karena investasi masa lalu yang tidak dapat ditarik kembali (sunk cost).\n\nSecara rasional, keputusan masa depan harus didasarkan pada prospek keuntungan masa depan, bukan pada apa yang telah hilang di masa lalu. Melanjutkan investasi buruk hanya akan menambah kerugian yang lebih besar.',
		example_id: 'Meskipun aplikasi ini terbukti memiliki banyak bug dan tidak disukai pengguna, kita harus terus mendanai pengembangannya karena kita sudah menghabiskan 500 juta rupiah untuk proyek ini.',
		how_to_counter: 'Tunjukkan bahwa uang 500 juta tersebut sudah hilang dan tidak bisa kembali. Fokuskan analisis pada potensi kerugian tambahan jika proyek tetap diteruskan dibanding jika dialihkan ke proyek baru.',
		severity: 'medium',
		category: 'causal',
		color_hex: '#8B0000',
		icon_emoji: '💸'
	}
];

export function getFallacyByCode(code: string): Fallacy | undefined {
	return FALLACIES.find((f) => f.code === code);
}

export function getFallaciesByCategory(category: string): Fallacy[] {
	return FALLACIES.filter((f) => f.category === category);
}

export function getFallacyColor(code: string): string {
	const fallacy = getFallacyByCode(code);
	return fallacy ? fallacy.color_hex : '#DA2B22';
}
