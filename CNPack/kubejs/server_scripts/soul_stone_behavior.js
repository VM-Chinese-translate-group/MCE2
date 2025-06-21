ItemEvents.rightClicked(event => {
    const { item, player, server, level } = event;
    if (!server || item.id !== 'kubejs:artifact_endergem') return;

    const name = player.username;
    const pos = player.blockPosition;

    player.getCooldowns().addCooldown('kubejs:artifact_endergem', 12000);

    server.runCommand(`tellraw ${name} {"text":"You peer into the Soul Stone and see a vision of The Great Beyond... Eternal darkness... Countless souls singing and dancing... Countless screaming and writhing.. It seems some take to death better than others.. ","italic":true,"color":"dark_gray"}`);
    server.runCommand(`execute at ${name} run playsound thegreatbelow:beacon_power_up ambient ${name}`);
    server.runCommand(`execute at ${name} run particle minecraft:soul ~ ~ ~`);


 player.potionEffects.add('thegreatbelow:soul_vision', 150, 0);    
 player.potionEffects.add('minecraft:darkness', 160, 0);    
    
    
});
