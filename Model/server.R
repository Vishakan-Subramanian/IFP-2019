# server.R
# link your Sheet's URL string here
googleSheet_embed_link <- ["https://docs.google.com/spreadsheets/d/1zHqrYxNQIblZuw92Db-uAaO-mlXTN4WFE3O8dq74aFY/edit#gid=0"]
shinyServer(function(input, output, session) {
  output$googleSheet <- renderUI({
    tags$iframe(id = "googleSheet",
                src = googleSheet_embed_link,
                width = 1024,
                height = 768,
                frameborder = 0,
                marginheight = 0)
  })
})