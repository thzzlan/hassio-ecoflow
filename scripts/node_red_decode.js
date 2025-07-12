// Helper functions for decoding EcoFlow packets inside Node‑RED.
// Place this file in a `function` node via the `require` statement and use the
// exported helpers to split incoming byte streams and decode PD packets.

// splitPackets(buf, context)
//  - buf: Buffer containing raw bytes from the device.
//  - context: node-red context object (e.g. `context` inside a function node).
// The function returns an array of complete protocol packets extracted from the
// stream. Any partial data is kept in context between calls.
function splitPackets(chunk, context) {
    let buf = context.get('ef_buf') || Buffer.alloc(0);
    buf = Buffer.concat([buf, chunk]);
    const packets = [];
    while (buf.length >= 4) {
        // look for packet header
        const idx = buf.indexOf(0xAA);
        if (idx === -1) {
            buf = Buffer.alloc(0);
            break;
        }
        if (idx > 0) {
            buf = buf.slice(idx);
        }
        if (buf.length < 4) break;
        if (buf[1] !== 0x02) {
            buf = buf.slice(1);
            continue;
        }
        const size = buf.readUInt16LE(2);
        if (buf.length < 18 + size) break;
        packets.push(buf.slice(0, 18 + size));
        buf = buf.slice(18 + size);
    }
    context.set('ef_buf', buf);
    return packets;
}


function decodePacket(buf) {
    // packet header: AA 02 00 00 CC (see integration source)
    if (buf[0] !== 0xAA || buf[1] !== 0x02) {
        throw new Error("invalid header");
    }
    const size = buf.readUInt16LE(2);
    if (buf.length < 18 + size) {
        throw new Error("packet too short");
    }
    let args = Buffer.from(buf.slice(16, 16 + size));
    if (((buf[5] >> 5) & 3) === 1) {
        for (let i = 0; i < args.length; i++) {
            args[i] ^= buf[6];
        }
    }
    return {
        dst: buf[12],
        cmdSet: buf[14],
        cmdId: buf[15],
        data: args,
    };
}

function parsePdDelta(data) {
    let off = 0;
    const res = {};
    const u8 = () => data.readUInt8(off++);
    const u16 = () => { const v = data.readUInt16LE(off); off += 2; return v; };
    const u32 = () => { const v = data.readUInt32LE(off); off += 4; return v; };
    const ver = () => [data[off+3], data[off+2], data[off+1], data[off]].join('.');
    const ver4 = () => { const v = ver(); off += 4; return v; };
    const tMin = () => { const v = u32(); return v; };
    const tSec = () => { const v = u32(); return v; };

    res.model = u8();
    res.pd_error = u32();
    res.pd_version = ver4();
    res.wifi_version = ver4();
    res.wifi_autorecovery = u8();
    res.battery_level = u8();
    res.out_power = u16();
    res.in_power = u16();
    res.remain_display = tMin();
    res.beep = u8();
    res._watts_anderson_out = u8();
    res.usb_out1_power = u8();
    res.usb_out2_power = u8();
    res.usbqc_out1_power = u8();
    res.usbqc_out2_power = u8();
    res.typec_out1_power = u8();
    res.typec_out2_power = u8();
    res.typec_out1_temp = u8();
    res.typec_out2_temp = u8();
    res.car_out_state = u8();
    res.car_out_power = u8();
    res.car_out_temp = u8();
    res.standby_timeout = u16();
    res.lcd_timeout = u16();
    res.lcd_brightness = u8();
    res.car_in_energy = u32();
    res.mppt_in_energy = u32();
    res.ac_in_energy = u32();
    res.car_out_energy = u32();
    res.ac_out_energy = u32();
    res.usb_time = tSec();
    res.typec_time = tSec();
    res.car_out_time = tSec();
    res.ac_out_time = tSec();
    res.ac_in_time = tSec();
    res.car_in_time = tSec();
    res.mppt_time = tSec();
    off += 2; // skip unknown
    res._ext_rj45 = u8();
    res._ext_infinity = u8();
    return res;
}

// Example Node-RED function node usage
// const dec = require('./scripts/node_red_decode');
// const packets = dec.splitPackets(msg.payload, context);
// for (const p of packets) {
//     const pkt = dec.decodePacket(p);
//     if (pkt.dst === 2 && pkt.cmdSet === 32 && pkt.cmdId === 2) {
//         node.send({payload: dec.parsePdDelta(pkt.data)});
//     }
// }
// return null;

module.exports = { splitPackets, decodePacket, parsePdDelta };
