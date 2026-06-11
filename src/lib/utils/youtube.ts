const VIDEO_ID_PATTERN = /^[a-zA-Z0-9_-]{11}$/;

export interface YoutubeVideoInfo {
	videoId: string;
	url: string;
	thumbnailUrl: string;
	embedUrl: string;
}

/**
 * Extracts the 11-character video ID from a YouTube URL.
 * Supports watch?v=, youtu.be/, shorts/, embed/, and /v/ formats.
 * Returns null if the URL is not a valid YouTube URL.
 */
export function extractVideoId(url: string): string | null {
	if (!url) return null;

	let parsed: URL;
	try {
		parsed = new URL(url.trim());
	} catch {
		return null;
	}

	const hostname = parsed.hostname.toLowerCase().replace(/^(www\.|m\.)/, '');

	if (hostname === 'youtu.be') {
		const id = parsed.pathname.slice(1).split('/')[0];
		return VIDEO_ID_PATTERN.test(id) ? id : null;
	}

	if (hostname === 'youtube.com' || hostname === 'youtube-nocookie.com') {
		const vParam = parsed.searchParams.get('v');
		if (vParam && VIDEO_ID_PATTERN.test(vParam)) return vParam;

		const pathMatch = parsed.pathname.match(/^\/(?:shorts|embed|v)\/([a-zA-Z0-9_-]{11})/);
		if (pathMatch) return pathMatch[1];
	}

	return null;
}

/** Returns true if the given URL is a valid YouTube URL with an extractable video ID. */
export function isValidYoutubeUrl(url: string): boolean {
	return extractVideoId(url) !== null;
}

/** Returns the max-resolution thumbnail URL for a video ID. */
export function getVideoThumbnail(videoId: string): string {
	return `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`;
}

/** Returns the canonical watch URL for a video ID. */
export function formatYoutubeUrl(videoId: string): string {
	return `https://www.youtube.com/watch?v=${videoId}`;
}

/** Returns the embed URL for a video ID, optionally starting at a given second. */
export function getEmbedUrl(videoId: string, startSeconds?: number): string {
	const base = `https://www.youtube.com/embed/${videoId}`;
	return startSeconds ? `${base}?start=${startSeconds}` : base;
}

/** Builds a YoutubeVideoInfo object from any supported YouTube URL, or null if invalid. */
export function getYoutubeVideoInfo(url: string): YoutubeVideoInfo | null {
	const videoId = extractVideoId(url);
	if (!videoId) return null;

	return {
		videoId,
		url: formatYoutubeUrl(videoId),
		thumbnailUrl: getVideoThumbnail(videoId),
		embedUrl: getEmbedUrl(videoId)
	};
}

/**
 * Examples (input -> output):
 *
 * extractVideoId('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
 *   -> 'dQw4w9WgXcQ'
 *
 * extractVideoId('https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s')
 *   -> 'dQw4w9WgXcQ'
 *
 * extractVideoId('https://youtu.be/dQw4w9WgXcQ')
 *   -> 'dQw4w9WgXcQ'
 *
 * extractVideoId('https://youtu.be/dQw4w9WgXcQ?t=10')
 *   -> 'dQw4w9WgXcQ'
 *
 * extractVideoId('https://www.youtube.com/shorts/dQw4w9WgXcQ')
 *   -> 'dQw4w9WgXcQ'
 *
 * extractVideoId('https://www.youtube.com/embed/dQw4w9WgXcQ')
 *   -> 'dQw4w9WgXcQ'
 *
 * extractVideoId('https://www.youtube.com/v/dQw4w9WgXcQ')
 *   -> 'dQw4w9WgXcQ'
 *
 * extractVideoId('https://example.com/watch?v=dQw4w9WgXcQ')
 *   -> null
 *
 * extractVideoId('not a url')
 *   -> null
 *
 * isValidYoutubeUrl('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
 *   -> true
 *
 * isValidYoutubeUrl('https://vimeo.com/12345')
 *   -> false
 *
 * getVideoThumbnail('dQw4w9WgXcQ')
 *   -> 'https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg'
 *
 * formatYoutubeUrl('dQw4w9WgXcQ')
 *   -> 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
 *
 * getEmbedUrl('dQw4w9WgXcQ')
 *   -> 'https://www.youtube.com/embed/dQw4w9WgXcQ'
 *
 * getEmbedUrl('dQw4w9WgXcQ', 90)
 *   -> 'https://www.youtube.com/embed/dQw4w9WgXcQ?start=90'
 *
 * getYoutubeVideoInfo('https://youtu.be/dQw4w9WgXcQ')
 *   -> {
 *        videoId: 'dQw4w9WgXcQ',
 *        url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
 *        thumbnailUrl: 'https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg',
 *        embedUrl: 'https://www.youtube.com/embed/dQw4w9WgXcQ'
 *      }
 */
