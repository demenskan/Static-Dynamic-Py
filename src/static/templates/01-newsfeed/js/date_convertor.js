function mddyyyy_to_mmmdyyyy(s) {
  var s = s.split(/\D/),
    dt = new Date(s[2], s[0] - 1, s[1]);
  return dt.toLocaleString('en-CA', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
}
