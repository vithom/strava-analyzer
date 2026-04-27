import panel as pn


def create_sidebar(pages, dataframe):
	page_selector = pn.widgets.Select(
		options={title: idx for idx, (title, _) in enumerate(pages)},
		value=0,
		sizing_mode="stretch_width",
	)

	def on_page_change(event):
		# tabs.active = event.new
		pass

	page_selector.param.watch(on_page_change, "value")

	return pn.Column(
		pn.pane.Markdown("## Pages"),
		page_selector,
		pn.pane.Markdown("---\n## Données", styles={"padding-top": "1em"}),
		pn.pane.Markdown(
			"Dernière activité : " + dataframe["Activity Date"].max().strftime("%d %b %Y"),
			styles={"color": "grey"},
		),
		pn.widgets.Button(
			name="Recharger les données",
			button_type="primary",
			sizing_mode="stretch_width",
		),
		pn.pane.Markdown("---\n## Filtres", styles={"padding-top": "1em"}),
		pn.widgets.MultiChoice(
			name="Sports",
			options=dataframe["Sport"].unique().tolist(),
			value=[],
			placeholder="Tous les sports",
			sizing_mode="stretch_width",
		),
	)
