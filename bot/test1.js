const ob = {
    key1: "val1",
    key2: "val2",
    f: function f() { return this.key1 }
        
    //"f": function(){ return Object.keys(this).join(', ')}(),
}
/*
function f() {
    return Object.keys(this).join(', ')
}*/

console.log(ob.f());