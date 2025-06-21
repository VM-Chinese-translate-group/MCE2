//credit to Atobá Azul in the latvian.dev discord server

PlayerEvents.inventoryChanged((event) => {
    if (!event.player.persistentData.waypointData) {
        event.player.persistentData.waypointData = [];
    }

    if (event.item.id === 'minecraft:filled_map') {
        //Turn nbt to object for easier handling here
        let nbt = JsonIO.toObject(NBT.toJson(event.item.nbt));
        let nbtString = event.item.nbtString; //NBT string for text formatting.

        let decorations = nbt.Decorations || [];
        let customDecorations = nbt.CustomDecorations || [];

        // Combine Decorations and CustomDecorations so we dont have to check for both individually.
        let allDecorations = decorations.concat(customDecorations);

        if (allDecorations.length > 0) {
            allDecorations.forEach((decoration) => {
                let { x, z } = decoration;

                // Checks if the waypoint already exists in the player's data, so we don't tell the player twice the same waypoint.
                let waypointExists =
                    event.player.persistentData.waypointData.some(
                        (waypoint) => waypoint.x === x && waypoint.z === z
                    );

                if (waypointExists) {
                    return;
                }

                // Default name - in case something's off.
                let name = 'Unknown';

                //Please excuse the mess here. I hate regex, so I did what I could to avoid it.
                // Extract the name from nbtString if it exists...
                if (nbtString.includes('"text"')) {
                    let temp = nbtString.split('"text":"')[1].split('"}')[0];
                    name = Component.of(temp.replace('"', '').split(' Map')[0]);
                }

                // ...or the translatable name
                if (nbtString.includes('"with"')) {
                    let temp = nbtString
                        .split('"with"')[1]
                        .split('"translate":')[1]
                        .split('}]}')[0];
                    name = Text.translate(temp.slice(1, -1));
                }

                //Send the player the waypoint
                let waypointText = Text.of('xaero-waypoint:')
                    .append(name)
                    .append(':X:')
                    .append(x.toString().slice(0, -2))
                    .append(':64:')
                    .append(z.toString().slice(0, -2))
                    .append(':3:false:0:Internal-overworld-waypoints');
                event.player.tell(waypointText);
                event.player.persistentData.waypointData.push({ x: x, z: z });
            });
        }
    }
});