// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

import type { PageLoad } from './$types';

export const load = (async ({ fetch }) => {
	const quiz_res = await fetch('/api/v1/quiz/list?page_size=100');
	let quizzes: unknown = [];
	if (quiz_res.ok) {
		quizzes = await quiz_res.json();
	}

	const quiztivity_res = await fetch('/api/v1/quiztivity/');
	let quiztivities: unknown = [];
	if (quiztivity_res.ok) {
		quiztivities = await quiztivity_res.json();
	}

	// Ensure we always return iterables to the page
	return {
		quizzes: Array.isArray(quizzes) ? quizzes : [],
		quiztivities: Array.isArray(quiztivities) ? quiztivities : []
	};
}) satisfies PageLoad;
