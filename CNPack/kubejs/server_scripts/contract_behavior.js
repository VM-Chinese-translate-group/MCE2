
ItemEvents.rightClicked(event => {
  const { item, player, server, hand } = event

  if (!server || item.id != 'kubejs:contract') return

  player.addItemCooldown(item, 25)

  player.runCommandSilent(
    `tellraw @s ` + JSON.stringify({
      text: "Contract: NO take backsies! §o(Hover to read small print)",
      italic: true,
      color: "gold",
      clickEvent: {
        action: "open_url",
        value: "https://www.youtube.com/watch?v=6vMrdTlwrIU"
      },
      hoverEvent: {
        action: "show_text",
        contents: [
          {
            text:
              "Small Print: Anything you ever create is proprietary property of ME and your soul is MINE... FOR ALL OF ETERNITY!! BARRY WITHHOLDS THE RIGHT TO DESTROY YOUR MORTAL COIL AT ANY GIVEN MOMENT.. THIS CONTRACT HAS BEEN SIGNED BY THE PLAYER AND IS LEGALLY BINDING IN MINECRAFT AND THE REAL WORLD!! The writing becomes so small its unreadable...",
            color: "gray"
          }
        ]
      }
    })
  )
})
